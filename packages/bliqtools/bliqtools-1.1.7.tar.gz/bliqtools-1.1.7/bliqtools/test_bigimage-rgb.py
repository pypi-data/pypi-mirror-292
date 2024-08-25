"""
Unit tests for BigImage with RGB tiles, a class to manipulate very large images
"""
import envtest
import unittest
import subprocess
from pathlib import Path
import tempfile
from contextlib import suppress

import numpy as np
import tifffile
from matplotlib import pyplot as plt
from PIL import Image

from bliqtools.nirvana import FilePath
from bliqtools.bigimage import BlockEntry, BigImage
from bliqtools.testing import MemoryMonitor, TimeIt, Progress


class TestRGBBigImage(envtest.TestCaseBigImage):  # pylint: disable=too-many-public-methods
    """
    Several tests for BigImage with RGB images and understanding its details
    """

    def test_00_datasetcreation(self):
        self.create_dataset()

    def test_01_init(self):
        """
        We can create a BigImage object
        """
        img = BigImage()
        self.assertIsNotNone(img)

    def test_02_add_rgb_block(self):
        """
        We can add an RGB block to a BigImage object
        """
        img = BigImage()
        small_block = np.ones(shape=(10, 10, 3), dtype=np.uint8)
        img.add_block(coords=(0, 0), data=small_block)
        self.assertEqual(len(img.entries), 1)

    def test_07_add_block_get_reduced_rgb_version(self):
        """
        Can we get a reduced version of a block? (in RGB)

        """

        img = BigImage()
        small_block = np.random.randint(0, 255, size=(10_000, 10_000, 3), dtype=np.uint8)
        img.add_block(coords=(0, 0), data=small_block)
        reduced_block = img.get_reduced_resolution_block((0, 0), factor=10)
        self.assertEqual(reduced_block.shape, (1000, 1000, 3))

    def test_08_get_reduced_rgb_preview(self):
        """
        Extract a reduced dimension preview from the BigImage in RGB
        """

        img = BigImage()
        with MemoryMonitor():
            with Progress(total=100, description="Tile") as p:
                for i in range(10):
                    for j in range(10):
                        small_block = np.full(
                            shape=(1_000, 1_000, 3), fill_value=10 * i + j, dtype=np.uint8
                        )
                        small_block[:,:,1] //= 2
                        small_block[:,:,1] //= 3

                        img.add_block(coords=(i * 1_000, j * 1_000), data=small_block)
                        p.next()

        preview = img.get_reduced_resolution_preview(factor=20)
        self.assertEqual(preview.shape, (500, 500, 3))
        plt.imshow(preview, interpolation="nearest")
        plt.title(self.current_test_name())
        image_path = Path(self.img_graph_path, self.current_test_name() + ".pdf")
        plt.savefig(image_path)

    def test_09_get_reduced_rgb_preview_with_overflow_in_overlap(self):
        """
        Extract a reduced dimension preview from the BigImage in RGB
        """

        img = BigImage()
        overlap = 250
        with MemoryMonitor():
            with Progress(total=100, description="Tile") as p:
                for i in range(2):
                    for j in range(2):
                        small_block = np.full(
                            shape=(1_000, 1_000, 3), fill_value=50 * i + 50*j, dtype=np.uint8
                        )
                        # small_block[:,:,1] //= 2
                        # small_block[:,:,1] //= 3

                        img.add_block(coords=(i * (1_000-overlap), j * (1_000-overlap)), data=small_block)
                        p.next()

        preview = img.get_reduced_resolution_preview(factor=20)
        # self.assertEqual(preview.shape, (500, 500, 3))
        plt.imshow(preview, interpolation="nearest")
        plt.title(self.current_test_name())
        image_path = Path(self.img_graph_path, self.current_test_name() + ".pdf")
        plt.savefig(image_path)

    def test_10_mask_is_same_all_channels(self):
        """
        Extract RGB
        """

        img = BigImage()
        overlap = 250
        small_block = np.full(
            shape=(1_000, 1_000, 3), fill_value=100, dtype=np.uint8
        )
        entry = BlockEntry(
            coords=(0,0),
            data=small_block)

        masks = entry.linear_overlap_masks(overlap_in_pixels=overlap)

        for i, group_mask in enumerate(masks):
            mask = group_mask[2]
            if mask.shape[2] == 2:
                self.assertTrue( (mask[:,:,0] == mask[:,:,1]).all() )
            if mask.shape[2] == 3:
                self.assertTrue( (mask[:,:,0] == mask[:,:,1]).all() )
                self.assertTrue( (mask[:,:,0] == mask[:,:,2]).all() )

            plt.imshow(mask, interpolation="nearest")
            plt.title(self.current_test_name())
            image_path = Path(self.img_graph_path, self.current_test_name() + f"-{i}.pdf")
            plt.savefig(image_path)

    def test_11_get_reduced_rgb_preview_with_masked_overlap(self):
        """
        Extract a reduced dimension preview from the BigImage in RGB
        """

        img = BigImage()
        overlap = 250
        mask = None
        with MemoryMonitor():
            with Progress(total=100, description="Tile") as p:
                for i in range(2):
                    for j in range(2):
                        small_block = np.full(
                            shape=(1_000, 1_000, 3), fill_value=50 * i + 50*j, dtype=np.uint8
                        )
                        entry = BlockEntry(
                            coords=(i * (1_000-overlap), j * (1_000-overlap)),
                            data=small_block)

                        if mask is None:
                            mask = entry.linear_overlap_mask(overlap_in_pixels=overlap)
                        entry.apply_mask(mask)

                        img.add_entry(entry)
                        p.next()

        preview = img.get_reduced_resolution_preview(factor=20)
        # self.assertEqual(preview.shape, (500, 500, 3))
        self.save_test_image_result(preview)



    def test_23_rgb_preview_with_global_mask_correction(self):
        """
        Third strategy, that will tunr out to be very successful:
        We calculate a mask for the whole block that tapers the edges to zero for
        smooth adddition to the map.  The glitch oberved by managing separate sub-blocks
        is gone because there are no sub-blocks.

        """
        BlockEntry.cache_previews_in_background = False
        BlockEntry.use_cache_previews = False
        img = BigImage()

        map_size = (17, 17)
        shape = (2048, 2048,3)
        overlap = 512

        mask = None

        with MemoryMonitor():
            with Progress(total=map_size[0] * map_size[1], description="Tile") as p:
                for i in range(map_size[0]):
                    for j in range(map_size[1]):
                        block = np.full(
                            shape=shape, fill_value=10 * i + 5 * j, dtype=np.uint8
                        )
                        entry = BlockEntry(
                            coords=(i * (shape[0] - overlap), j * (shape[1] - overlap)),
                            data=block,
                        )
                        if mask is None:
                            mask = entry.linear_overlap_mask(overlap_in_pixels=overlap)
                        entry.apply_mask(mask)
                        img.add_entry(entry)
                        p.next()

        preview = img.get_reduced_resolution_preview(factor=64)
        plt.imshow(preview)
        plt.title(self.current_test_name())
        image_path = Path(self.img_graph_path, self.current_test_name() + ".pdf")
        plt.savefig(image_path)



if __name__ == "__main__":
    unittest.main()
    # unittest.main(
    #     defaultTest=["TestBigImage.test_30_what_is_the_exception_with_tifffile"]
    # )
