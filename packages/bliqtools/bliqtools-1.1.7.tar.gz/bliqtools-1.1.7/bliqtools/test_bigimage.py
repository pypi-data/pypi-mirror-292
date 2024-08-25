"""
Unit tests for BigImage, a class to manipulate very large images
"""

import envtest
import unittest
import subprocess
import shutil
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


class TestBigImage(envtest.TestCaseBigImage):  # pylint: disable=too-many-public-methods
    """
    Several tests for BigImage and understanding its details
    """

    def test_01_init(self):
        """
        We can create a BigImage object
        """
        img = BigImage()
        self.assertIsNotNone(img)

    def test_02_add_block(self):
        """
        We can add a block to a BigImage object
        """
        img = BigImage()
        small_block = np.ones(shape=(10, 10), dtype=np.uint8)
        img.add_block(coords=(0, 0), data=small_block)
        self.assertEqual(len(img.entries), 1)

    def test_03_tempdir(self):
        """
        Understanding how tempfile.TemporaryDirectory() works.
        We need to keep the reference to the object, will
        not use it for now.
        """
        tdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        tdir.cleanup()

    def test_04_add_many_blocks(self):
        """
        We can add a block to a BigImage object
        """

        img = BigImage()
        with MemoryMonitor():
            with Progress(total=100, description="Block") as p:
                for i in range(10):
                    for j in range(10):
                        small_block = np.random.randint(
                            0, 255, size=(10_00, 10_00), dtype=np.uint8
                        )
                        img.add_block(coords=(i, j), data=small_block)
                        p.next()

        self.assertEqual(len(img.entries), 100)

    def test_05_purge_actually_clears_memory(self):
        """
        We can add a block to a BigImage object
        """

        img = BigImage()
        small_block = np.random.randint(0, 255, size=(10_00, 10_00), dtype=np.uint8)
        img.add_block(coords=(0, 0), data=small_block)

        self.assertFalse(img.entries[0].is_purged)

        img.entries[0].purge(img._work_dir.name)

        self.assertTrue(img.entries[0].is_purged)

    def test_06_add_many_blocks_with_purge(self):
        """
        We can add a block to a BigImage object
        """

        img = BigImage()
        with MemoryMonitor():
            with Progress(total=100, description="Tile") as p:
                for i in range(10):
                    for j in range(10):
                        small_block = np.zeros(shape=(10_000, 10_000), dtype=np.uint8)
                        img.add_block(coords=(i * 10_000, j * 10_000), data=small_block)
                        p.next()
                    img.purge_if_needed()

        self.assertEqual(len(img.entries), 100)

    def test_07_add_block_get_reduced_version(self):
        """
        Can we get a reduced version of a block?

        """

        img = BigImage()
        small_block = np.random.randint(0, 255, size=(10_000, 10_000), dtype=np.uint8)
        img.add_block(coords=(0, 0), data=small_block)
        reduced_block = img.get_reduced_resolution_block((0, 0), factor=10)
        self.assertEqual(reduced_block.shape, (1000, 1000, 1))

    def test_08_get_reduced_preview(self):
        """
        Extract a reduced dimension preview from the BigImage
        """

        img = BigImage()
        with MemoryMonitor():
            with Progress(total=100, description="Tile") as p:
                for i in range(10):
                    for j in range(10):
                        small_block = np.full(
                            shape=(1_000, 1_000), fill_value=10 * i + j, dtype=np.uint8
                        )
                        img.add_block(coords=(i * 1_000, j * 1_000), data=small_block)
                        p.next()

        preview = img.get_reduced_resolution_preview(factor=20)
        self.assertEqual(preview.shape, (500, 500, 1))
        self.save_test_image_result(preview)

    def test_09_get_reduced_preview_missing_blocks(self):
        """
        Extract a reduced dimension preview from the BigImage
        """

        img = BigImage()
        with MemoryMonitor():
            with Progress(total=100, description="Tile") as p:
                for i in range(10):
                    for j in range(i):
                        small_block = np.full(
                            shape=(1_000, 1_000), fill_value=10 * i + j, dtype=np.uint8
                        )
                        img.add_block(coords=(i * 1_000, j * 1_000), data=small_block)
                        p.next()

        self.assertEqual(img.calculate_size(), (10000, 9000, 1))
        preview = img.get_reduced_resolution_preview(factor=20)
        self.assertEqual(preview.shape, (500, 450, 1))

        self.save_test_image_result(preview)

    def test_11_pil_thumbnail(self):
        """
        PIL offers a function to create a thumbnail of an image.
        Unfortunately, this is not faster than either numpy slicing or scipy
        """
        root_dir = FilePath(self.dataset_grayscale)
        filepaths = root_dir.contents()

        layer1_filepaths = [filepath for filepath in filepaths if filepath.k == 1]
        some_filepath = layer1_filepaths[0]
        with TimeIt():
            with Image.open(some_filepath) as im:
                _ = im.thumbnail((64, 64))

    def reslice_block(self, coords, block, cut_indexes, axis):
        """
        Function used for development of the test below.
        """
        sub_blocks = np.split(block, cut_indexes, axis=axis)

        start_pos = [0]
        start_pos.extend(cut_indexes)

        blocks_with_positions = []
        for i, sub_block in enumerate(sub_blocks):
            sub_block_coords = list(coords)
            sub_block_coords[axis] += start_pos[i]
            blocks_with_positions.append((sub_block, tuple(sub_block_coords)))

        return blocks_with_positions

    def test_breakup_tiles_in_smaller_tiles_from_overlap(self):
        """
        Attempt at managing overlap by breaking down tiles in smaller tiles.
        As will be seen below, this is not the best strategy and leaves many artifacts
        in the final image.

        This test is one of the first step in that direction.
        """
        small_block = np.full(shape=(1_024, 1_024), fill_value=128, dtype=np.uint8)

        overlap_in_pixels = 100
        sub_tiles = np.split(
            small_block, [overlap_in_pixels, 1024 - overlap_in_pixels], axis=0
        )
        self.assertEqual(len(sub_tiles), 3)
        self.assertEqual(sub_tiles[0].shape, (overlap_in_pixels, 1024))
        self.assertEqual(sub_tiles[1].shape, (1024 - 2 * overlap_in_pixels, 1024))
        self.assertEqual(sub_tiles[2].shape, (overlap_in_pixels, 1024))
        all_sub_tiles = []
        for sub_tile in sub_tiles:
            all_sub_tiles.extend(
                np.split(
                    sub_tile, [overlap_in_pixels, 1024 - overlap_in_pixels], axis=1
                )
            )

    def test_reslice_blockentries(self):
        """
        Attempt at managing overlap by breaking down tiles in smaller tiles.
        As will be seen below, this is not the best strategy and leaves many artifacts
        in the final image.

        This test is the third step in that direction.
        """

        data = np.full(shape=(1_024, 1_024), fill_value=128, dtype=np.uint8)
        start_entry = BlockEntry(coords=(0, 0), data=data)
        entries = start_entry.cut_block(cut_indexes=[100, 924], axis=0)

        axis = 0
        for i in [0, 1]:
            entry = entries[i]
            next_entry = entries[i + 1]
            self.assertEqual(
                entry.coords[axis] + entry.data.shape[axis], next_entry.coords[axis]
            )

        axis = 1
        for entry in entries:
            cut_entries = entry.cut_block(cut_indexes=[100, 924], axis=1)
            for i in [0, 1]:
                entry = cut_entries[i]
                next_entry = cut_entries[i + 1]
                self.assertEqual(
                    entry.coords[axis] + entry.data.shape[axis], next_entry.coords[axis]
                )

    def test_reslice_blockentries_negative_cut_from_end(self):
        """
        Attempt at managing overlap by breaking down tiles in smaller tiles.
        As will be seen below, this is not the best strategy and leaves many artifacts
        in the final image.

        Here, provide negative indices for the right so we don't need to know the size of the block we cut
        """
        data = np.full(shape=(1_024, 1_024), fill_value=128, dtype=np.uint8)
        start_entry = BlockEntry(coords=(0, 0), data=data)
        entries = start_entry.cut_block(cut_indexes=[100, -100], axis=0)

        axis = 0
        for i in [0, 1]:
            entry = entries[i]
            next_entry = entries[i + 1]
            self.assertEqual(
                entry.coords[axis] + entry.data.shape[axis], next_entry.coords[axis]
            )

        axis = 1
        for entry in entries:
            cut_entries = entry.cut_block(cut_indexes=[100, -100], axis=1)
            for i in [0, 1]:
                entry = cut_entries[i]
                next_entry = cut_entries[i + 1]
                self.assertEqual(
                    entry.coords[axis] + entry.data.shape[axis], next_entry.coords[axis]
                )

    def test_20_preview_with_cut_blocks(self):
        """
        A small digression that turned out to be not so useful: cahcing a preview.

        When loading entries directly with data, the BlockEntry class
        will keep a preview reduced by a factor 16.  Making the preview will be really fast.

        However, if we perform computation on the block, then the cached preview interferes.

        """

        img = BigImage()
        overlap = 400
        with MemoryMonitor():
            with Progress(total=100, description="Tile") as p:
                for i in range(4):
                    for j in range(4):
                        small_block = np.full(
                            shape=(2048, 2048),
                            fill_value=20 * i + 5 * j,
                            dtype=np.uint8,
                        )
                        entry = BlockEntry(
                            coords=(i * (2048 - overlap), j * (2048 - overlap)),
                            data=small_block,
                        )
                        entry_strips = entry.cut_block(
                            cut_indexes=[overlap, -overlap], axis=0
                        )

                        entry_strips[0].data //= 2
                        entry_strips[2].data //= 2

                        cut_entries = []
                        for entry_strip in entry_strips:
                            strip_cuts = entry_strip.cut_block(
                                cut_indexes=[overlap, -overlap], axis=1
                            )
                            strip_cuts[0].data //= 2
                            strip_cuts[2].data //= 2
                            cut_entries.extend(strip_cuts)

                        for entry in cut_entries:
                            img.add_entry(entry)
                        p.next()

        preview = img.get_reduced_resolution_preview(factor=4)
        self.save_test_image_result(preview)

    def test_21_preview_with_cut_overlap_blocks(self):
        """
        Now that all necessary functions have been created and tested,
        this is the real first attempt(eventually unsuccessful) to try to cut the block in sub-blocks to manage
        each overlap section individually.

        Here, I test a simple average (divide by 2 for edges and 4 for corners).

        Unfortunately, applying the reduction on small blocks may result in glitches at the edges
        if the overlap length is not a multiple of the reduction factor, or if the block size
        is not a multiple either.  Overall, bad idea to split the block to treat them,
        the next tests will apply the mask directly onto the whole block.

        It is quite obvious in the final figure shown/saved.

        """

        img = BigImage()
        overlap = 100

        with MemoryMonitor():
            with Progress(total=100, description="Tile") as p:
                for i in range(10):
                    for j in range(10):
                        small_block = np.full(
                            shape=(2048, 2048),
                            fill_value=20 * i + 5 * j,
                            dtype=np.uint8,
                        )
                        entry = BlockEntry(
                            coords=(i * (2048 - overlap), j * (2048 - overlap)),
                            data=small_block,
                        )
                        overlapped_entries = entry.get_overlap_blocks(overlap=overlap)

                        overlapping_labels = list(overlapped_entries.keys())
                        overlapping_labels.remove("00")  # center

                        for label in overlapping_labels:
                            if label in ["++", "--", "-+", "+-"]:  # Need to correct 2x
                                correction = 4
                            else:
                                correction = 2
                            entry = overlapped_entries[label]
                            entry.data //= correction
                            overlapped_entries[label] = entry

                        for label, entry in overlapped_entries.items():
                            img.add_entry(entry)
                        p.next()

        preview = img.get_reduced_resolution_preview(factor=32)
        self.save_test_image_result(preview)

    def test_22_preview_with_cut_overlap_blocks_linear_correction(
        self,
    ):  # pylint: disable=too-many-locals
        """
        Second attempt (also unsuccessful) to try to cut the block in sub-blocks to manage
        each overlap section individually. Here, I test a linear factor but the same problem described here
        is also apparent: applying the reduction on small blocks may result in glitches at the edges
        if the overlap length is not a multiple of the reduction factor, or if the block size
        is not a multiple either.  Overall, bad idea to split the block to treat them,
        the next tests will apply the mask directly onto the whole block.

        """
        BlockEntry.cache_previews_in_background = False
        BlockEntry.use_cache_previews = False
        img = BigImage()

        overlap = 512
        with MemoryMonitor():
            with Progress(total=100, description="Tile") as p:
                for i in range(4):
                    for j in range(4):
                        block = np.full(
                            shape=(2048, 2048),
                            fill_value=20 * i + 5 * j,
                            dtype=np.uint8,
                        )
                        entry = BlockEntry(
                            coords=(i * (2048 - overlap), j * (2048 - overlap)),
                            data=block,
                        )
                        overlapping_entries = entry.get_overlap_blocks(overlap=overlap)

                        for label, _ in overlapping_entries.items():
                            over_entry = overlapping_entries[label]

                            shape = over_entry.data.shape
                            mask = np.ones(shape=shape, dtype=np.float16)
                            if label[0] == "+":
                                for c in range(shape[2]):
                                    for k in range(shape[1]):
                                        mask[:, k, c] = np.array(np.linspace(1, 0, shape[0]))
                            elif label[0] == "-":
                                for c in range(shape[2]):
                                    for k in range(shape[1]):
                                        mask[:, k, c] = np.array(np.linspace(0, 1, shape[0]))

                            if label[1] == "+":
                                for c in range(shape[2]):
                                    for k in range(shape[0]):
                                        mask[k, :, c] *= np.array(np.linspace(1, 0, shape[1]))
                            elif label[1] == "-":
                                for c in range(shape[2]):
                                    for k in range(shape[0]):
                                        mask[k, :, c] *= np.array(np.linspace(0, 1, shape[1]))

                            over_entry.data = np.multiply(over_entry.data, mask).astype(
                                np.uint8
                            )

                            img.add_entry(over_entry)

                        # for label, entry in overlapped_entries.items():
                        #     img.add_entry(entry)
                        p.next()

        preview = img.get_reduced_resolution_preview(factor=8)
        self.save_test_image_result(preview)

    def test_23_preview_with_global_mask_correction(self):
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
        shape = (2048, 2048)
        overlap = 512

        mask = None

        with MemoryMonitor():
            with Progress(total=map_size[0] * map_size[1], description="Tile") as p:
                for i in range(map_size[0]):
                    for j in range(map_size[1]):
                        block = np.full(
                            shape=shape, fill_value=20 * i + 5 * j, dtype=np.uint16
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
        self.save_test_image_result(preview)

    def test_28_partial_masks(self):
        """
        Test to use partial masks instead of full mask on blocks.
        It is significantly faster because it performs 50% less calculations at least.
        (Only on overlap, not full image)
        """
        overlap = 200
        shape = (2048, 2048,1)
        block = np.full(shape=shape, fill_value=128, dtype=np.uint8)
        entry = BlockEntry(
            coords=(0, 0),
            data=block,
        )
        masks = entry.linear_overlap_masks(overlap)
        entry.apply_partial_masks(masks)


        self.save_test_image_result(entry.data)

    def test_30_what_is_the_exception_with_tifffile(self):
        """
        Need to understand the exact type of tifffile imread exception
        """
        try:
            tifffile.imread(__file__)
        except tifffile.TiffFileError:
            return
        except Exception:
            self.fail("Exception type is not tifffile.TiffFileError")


def compute_previews(entry):
    """
    Function used in the multiprocessing example
    """
    for factor in [16, 32, 64, 128]:
        preview = entry.get_preview(factor=factor)
        entry.previews[factor] = preview


if __name__ == "__main__":
    unittest.main()
    # unittest.main(
    #     defaultTest=["TestBigImage.test_30_what_is_the_exception_with_tifffile"]
    # )
