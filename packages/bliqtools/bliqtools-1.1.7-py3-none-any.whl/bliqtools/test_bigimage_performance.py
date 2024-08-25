"""
Perfomance Unit tests for BigImage, a class to manipulate very large images
"""

import envtest
import unittest
import cProfile
from multiprocessing import Pool, cpu_count
from collections import deque
import subprocess
import shutil
from pathlib import Path
from threading import Thread
import tempfile
from contextlib import suppress

import numpy as np
import tifffile
from matplotlib import pyplot as plt
import psutil
from PIL import Image

from bliqtools.nirvana import FilePath
from bliqtools.bigimage import BlockEntry, BigImage
from bliqtools.testing import MemoryMonitor, TimeIt, Progress


class TestRGBBigImage(envtest.TestCaseBigImage):  # pylint: disable=too-many-public-methods
    """
    Several tests for BigImage and understanding its details
    """


    def cheap_tile_loader_knock_off(self, filepaths):
        """
        This function mimicks the behaviour of TileLoader because I do not want to import it
        for testing here.

        Returns the number of tiles in i,j,k
        """
        i = set()
        j = set()
        k = set()
        for filepath in filepaths:
            i.add(filepath.i)
            j.add(filepath.j)
            k.add(filepath.k)

        some_filepath = filepaths[0]
        some_entry = BlockEntry(coords=(0, 0), data=None, image_filepath=some_filepath)
        w, h, c = some_entry.data.shape

        return len(i), len(j), len(k), w, h, c

    def test_10_from_real_dataset_attempt(self):
        """
        This assumes a dataset at path, with Nirvana-style tiles.
        We work with the first layer only.
        """
        root_dir = FilePath(self.dataset_grayscale)
        filepaths = root_dir.contents()
        layer1_filepaths = [filepath for filepath in filepaths if filepath.k == 1]
        _, _, _, w, h, c = self.cheap_tile_loader_knock_off(layer1_filepaths)

        img = BigImage()
        with TimeIt(description="Real dataset"):
            with Progress(total=len(layer1_filepaths)) as p:
                for filepath in layer1_filepaths:
                    pixel_x = (filepath.i - 1) * w
                    pixel_y = (filepath.j - 1) * h

                    entry = BlockEntry(
                        coords=(pixel_x, pixel_y), data=None, image_filepath=filepath
                    )
                    img.add_entry(entry)
                    p.next()
            with cProfile.Profile() as profiler:
                with MemoryMonitor():
                    preview = img.get_reduced_resolution_preview(factor=32)
                    profiler.print_stats("time")

        self.save_test_image_result(preview)

    def test_12_tifffile_writes_images_as_tiles(self):
        """
        Tifffile can write "tiled" images. This attempts to use the feature
        to try to see if it means what I think it means, but when the file
        is opened, I see multiple pages, nto a single image.
        Not sure what to do with this.
        """
        data = np.random.rand(2, 5, 3, 301, 219).astype("float32")
        with tempfile.TemporaryDirectory() as td:
            tifffile.imwrite(
                Path(td, "temp.tif"),
                data,
                bigtiff=True,
                photometric="rgb",
                planarconfig="separate",
                tile=(32, 32),
                compression="zlib",
                compressionargs={"level": 8},
                predictor=True,
                metadata={"axes": "TZCYX"},
            )

    def test_13_get_fast_preview_from_cache(self):
        """
        When loading entries directly with data, the BlockEntry class
        will keep a preview reduced by a factor 16.  Making the preview will be really fast

        """

        img = BigImage()
        with MemoryMonitor():
            with Progress(total=100, description="Tile") as p:
                for i in range(10):
                    for j in range(10):
                        small_block = np.full(
                            shape=(1_024, 1_024), fill_value=10 * i + j, dtype=np.uint8
                        )
                        img.add_block(coords=(i * 2048, j * 2048), data=small_block)
                        p.next()

        preview = img.get_reduced_resolution_preview(factor=32)
        self.save_test_image_result(preview)

    @unittest.skip("No gain at all from calculating in parallel.")
    def test_14_compute_previews_in_parallel(self):
        """
        This assumes a dataset at path, with Nirvana-style tiles.
        We work with the first layer only.
        """

        root_dir = FilePath(Path.home(), "Downloads/Test_maps/C1")
        filepaths = root_dir.contents()
        layer1_filepaths = [filepath for filepath in filepaths if filepath.k == 1]
        _, _, _, w, h = self.cheap_tile_loader_knock_off(layer1_filepaths)

        img = BigImage()

        for filepath in layer1_filepaths:
            pixel_x = (filepath.i - 1) * w
            pixel_y = (filepath.j - 1) * h

            entry = BlockEntry(
                coords=(pixel_x, pixel_y), data=None, image_filepath=filepath
            )
            img.add_entry(entry)

        with TimeIt():
            for entry in img.entries:
                compute_previews(entry)

        with TimeIt():
            with Pool(5) as p:
                p.map(compute_previews, img.entries)

    def test_24_from_real_dataset_attempt(self):
        """
        We test this strategy of a mask applied on each block with a real dataset.
        """
        root_dir = FilePath(self.dataset_grayscale)
        filepaths = root_dir.contents()
        layer1_filepaths = [filepath for filepath in filepaths if filepath.k == 1]
        _, _, _, w, h,c = self.cheap_tile_loader_knock_off(layer1_filepaths)

        img = BigImage()
        overlap = 250
        masks = None
        with cProfile.Profile() as profiler:
            with TimeIt(description="Real dataset building with mask"):
                with Progress(total=len(layer1_filepaths)) as p:
                    for filepath in layer1_filepaths:
                        pixel_x = (filepath.i - 1) * (w - overlap)
                        pixel_y = (filepath.j - 1) * (h - overlap)

                        entry = BlockEntry(
                            coords=(pixel_x, pixel_y),
                            data=None,
                            image_filepath=filepath,
                        )

                        if masks is None:
                            masks = entry.linear_overlap_masks(
                                overlap_in_pixels=overlap
                            )

                        entry.apply_partial_masks(masks)
                        img.add_entry(entry)
                        p.next()
        profiler.print_stats("time")

        preview = img.get_reduced_resolution_preview(factor=8)

        self.save_test_image_result(preview)

    @unittest.skip("This is a very lengthy test (2 minutes). Uncomment to run")
    def test_25_from_real_3d_dataset(self):
        """
        The ultimate test: a very large 3D dataset.
        You should have a big dataset in Downloads/Test_maps/C1

        """
        root_dir = FilePath(Path.home(), "Downloads/Test_maps/C1")
        filepaths = root_dir.contents()

        _, _, nk, w, h = self.cheap_tile_loader_knock_off(filepaths)
        overlap = 250
        mask = None
        with tempfile.TemporaryDirectory() as td:
            with MemoryMonitor() as m:
                with TimeIt(description="Real dataset building with mask"):
                    with Progress(description="Completing layer", total=nk) as p:
                        for k in range(1, nk + 1):
                            img = BigImage()
                            layer_k_filepaths = [
                                filepath for filepath in filepaths if filepath.k == k
                            ]
                            print(f"Mapping layer {k}")
                            for filepath in layer_k_filepaths:
                                pixel_x = (filepath.i - 1) * (w - overlap)
                                pixel_y = (filepath.j - 1) * (h - overlap)

                                entry = BlockEntry(
                                    coords=(pixel_x, pixel_y),
                                    data=None,
                                    image_filepath=filepath,
                                )

                                if mask is None:
                                    mask = entry.linear_overlap_mask(
                                        overlap_in_pixels=overlap
                                    )

                                entry.apply_mask(mask)
                                img.add_entry(entry)
                            p.next()

                            preview = img.get_reduced_resolution_preview(factor=1)
                            tifffile.imwrite(Path(td, f"Layer-{k}.tif"), preview, bigtiff=True)

                            self.save_test_image_result(preview)

                m.report_stats()

    @unittest.skip("This is a very lengthy test (2 minutes). Uncomment to run")
    def test_26_from_real_3d_dataset_one_big_tiff(self):
        """
        Again with a large 3D dataset, now save all layers in a single TIFF using the
        contiguous=True option and a contextmanager with tifffile ... as tif:
        """
        root_dir = FilePath(self.dataset_grayscale)
        filepaths = root_dir.contents()

        _, _, nk, w, h = self.cheap_tile_loader_knock_off(filepaths)
        overlap = 250
        mask = None
        with tifffile.TiffWriter(f"/tmp/Big_Image.tif", bigtiff=True) as tif:
            with MemoryMonitor() as m:
                with TimeIt(description="Real dataset building with mask"):
                    with Progress(
                        description="Completing layer",
                        total=nk,
                    ) as p:
                        for k in range(1, nk + 1):
                            img = BigImage()
                            layer_k_filepaths = [
                                filepath for filepath in filepaths if filepath.k == k
                            ]
                            print(f"Mapping layer {k}")
                            for filepath in layer_k_filepaths:
                                pixel_x = (filepath.i - 1) * (w - overlap)
                                pixel_y = (filepath.j - 1) * (h - overlap)

                                entry = BlockEntry(
                                    coords=(pixel_x, pixel_y),
                                    data=None,
                                    image_filepath=filepath,
                                )

                                if mask is None:
                                    mask = entry.linear_overlap_mask(
                                        overlap_in_pixels=overlap
                                    )

                                entry.apply_mask(mask)
                                img.add_entry(entry)
                            p.next()

                            preview = img.get_reduced_resolution_preview(factor=1)
                            tif.write(preview, contiguous=True)
                            self.save_test_image_result(preview)

                m.report_graph()

    def test_26_from_real_3d_dataset_save_layers_in_thread(self):
        """
        Is it faster to save in a separate thread?

        Short answer: no.

        """
        root_dir = FilePath(self.dataset_grayscale)
        filepaths = root_dir.contents()

        _, _, nk, w, h,c  = self.cheap_tile_loader_knock_off(filepaths)
        overlap = 250
        masks = None
        with tempfile.TemporaryDirectory() as td:
            with MemoryMonitor() as m:
                with TimeIt(description="Real dataset building with mask"):
                    with Progress(
                        description="Completing layer",
                        total=nk,
                    ) as p:
                        for k in range(1, nk // 3 + 1):
                            img = BigImage()
                            layer_k_filepaths = [
                                filepath for filepath in filepaths if filepath.k == k
                            ]
                            print(f"Mapping layer {k}")
                            for filepath in layer_k_filepaths:
                                pixel_x = (filepath.i - 1) * (w - overlap)
                                pixel_y = (filepath.j - 1) * (h - overlap)

                                entry = BlockEntry(
                                    coords=(pixel_x, pixel_y),
                                    data=None,
                                    image_filepath=filepath,
                                )

                                if masks is None:
                                    masks = entry.linear_overlap_masks(
                                        overlap_in_pixels=overlap
                                    )

                                entry.apply_partial_masks(masks)
                                img.add_entry(entry)
                            p.next()

                            preview = img.get_reduced_resolution_preview(factor=1)
                            thread = Thread(
                                target=tifffile.imwrite,
                                args=(Path(td, f"Layer-{k}.tif"), preview),
                                kwargs={"bigtiff": True},
                            )
                            thread.start()

                            self.save_test_image_result(preview)

            m.report_graph()

    def test_27_one_layer_one_thread(self):
        """
        Is it faster to do each layer in its own thread?
        The number of thread is hard to estimate: it depends on available cores and memory.

        """
        root_dir = FilePath(self.dataset_grayscale)
        filepaths = root_dir.contents()

        _, _, nk, w, h, c = self.cheap_tile_loader_knock_off(filepaths)
        overlap = 200
        factor = 1
        thread = None

        available_mem = psutil.virtual_memory().available / 1e9
        approximate_task = available_mem // 2

        with tempfile.TemporaryDirectory() as td:
            for k in range(1, nk + 1):
                layer_filepath = Path(td, f"Layer-{k}.tif")
                layer_k_filepaths = [filepath for filepath in filepaths if filepath.k == k]

                thread = Thread(
                    target=build_one_layer,
                    args=(layer_k_filepaths, k, w, h,c, overlap, factor, layer_filepath),
                )
                thread.start()

                if k % approximate_task == 0:
                    thread.join()

            thread.join()

    def test_29_use_worker_threads_and_deque(self):
        """
        Use worker threads to go through the queue of data to process.
        We allow 4 threads because we have 4 to 8 cores but other processes
        need to run too.
        """

        root_dir = FilePath(self.dataset_grayscale)
        filepaths = root_dir.contents()
        _, _, nk, w, h,c  = self.cheap_tile_loader_knock_off(filepaths)
        overlap = 200
        factor = 1

        with tempfile.TemporaryDirectory() as td:
            # Fill the queue with data
            queue = deque()  # a deque is MUCH faster and simpler than a Queue
            for k in range(1, nk + 1):
                layer_k_filepaths = [filepath for filepath in filepaths if filepath.k == k]
                layer_filepath = Path(td, f"Layer-{k}.tif")
                queue.appendleft(
                    (layer_k_filepaths, k, w, h,c, overlap, factor, layer_filepath)
                )

            # Start the worker threads
            thread = None
            for _ in range(cpu_count() // 4):
                thread = Thread(target=layer_builder_worker_thread, args=(queue,))
                thread.start()

            thread.join()


def layer_builder_worker_thread(queue):
    """
    Small worker thread that will take data if available to build one layer,
    ifno data available it quits.
    """
    while True:
        try:
            args = queue.pop()
            # Reusing the same function as previous test
            build_one_layer(*args)
        except IndexError:
            break


def build_one_layer(filepaths, k, w, h, c, overlap, factor, layer_filepath):
    """
    With all the filepaths making up a layer, this function builds the preview of
    the image at 'factor' reduction and saves it to layer_filepath
    """
    masks = None
    img = BigImage()
    layer_k_filepaths = filepaths
    print(f"Building layer {k}")
    with Progress(total=len(layer_k_filepaths), description=f"Layer {k} progress") as p:
        for filepath in layer_k_filepaths:
            pixel_x = (filepath.i - 1) * (w - overlap)
            pixel_y = (filepath.j - 1) * (h - overlap)

            entry = BlockEntry(
                coords=(pixel_x, pixel_y),
                data=None,
                image_filepath=filepath,
            )

            if overlap > 0:
                if masks is None:
                    masks = entry.linear_overlap_masks(overlap_in_pixels=overlap)

                entry.apply_partial_masks(masks)

            img.add_entry(entry)
            img.purge_if_needed()
            p.next()

    print(f"Starting preview for layer {k} at factor {factor}")
    preview = img.get_reduced_resolution_preview(factor=factor)
    tifffile.imwrite(layer_filepath, preview, bigtiff=True)


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
