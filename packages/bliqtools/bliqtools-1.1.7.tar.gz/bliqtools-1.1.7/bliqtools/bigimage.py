"""
The purpose of the BigImage class is to provide a method to manage and display a very Big Image
without having to worry too much about the memory restrictions. The image is constructed
by placing blocks of pixels at their positions (i.e. the top corner of the block). 
The class BigImage will return a preview decimated (i.e. reduced) by 'factor' (an integer) to make it manageable
and possible to display reasonably well.  It makes it possible to work with an image that would be several GB without 
sacrificing speed: for instance, and image of 1 GB made of 17x17x2048x2048 images can be displayed in less than a second.

"""

import tempfile
import time
from pathlib import Path
from threading import Thread, RLock

import numpy as np
from PIL import Image
import tifffile
import psutil

from bliqtools.testing import Progress


class BlockEntry:
    """Class for keeping track of an image block, either on disk or in memory.
    An image block is a section of the image (i.e. a numpy array) with its top corner.
    The entry will have its data either in the data property, or on disk, not both.
    """

    cache_previews_in_background = False
    use_cache_previews = False

    def __init__(self, coords, data, image_filepath=None):
        """
        Initialize the entry with the corner coords and the data or the image filepath.
        If we have the data immediately, then we compute previews with a group of useful
        factors since it is not expensive to do so.
        """
        self.coords = coords
        self._data = data
        self._fix_data_shape_if_needed()

        self.image_filepath = image_filepath
        self._saved_filepath = None
        self.last_access = None
        self.previews = {}
        self._lock = RLock()

        self._shape = None
        if self._data is not None:
            self._shape = self._data.shape


        if self._data is not None:
            self.cache_previews(factors=[16, 32, 64])
        elif BlockEntry.cache_previews_in_background:
            thread = Thread(target=self.cache_previews)
            thread.start()

    def cache_previews(self, factors=None):
        """
        Computes the preview for a given factor and stores them.
        You may need to invalidate the cache manually if you use it.
        """
        with self._lock:
            if BlockEntry.use_cache_previews:
                if factors is None:
                    factors = [16, 32, 64]
                for factor in factors:
                    self.previews[factor] = self.get_preview(factor=factor)

    @property
    def is_purged(self):
        """
        True if the data is not in memory
        """
        with self._lock:
            return self._data is None

    def _fix_data_shape_if_needed(self):
        if self._data is not None:
            if len(self._data.shape) == 2:
                self._data = np.reshape(self._data, newshape=(self._data.shape[0], self._data.shape[1], 1))

    @property
    def data(self):
        """
        Return the numpy data of the entry. If it is not already loaded,
        obtain it from the _saved_filepath if it has been set, or from
        the image_filepath that was passed on init.
        """
        with self._lock:
            if self.is_purged:
                if self._saved_filepath is not None:
                    self._data = np.load(self._saved_filepath)
                else:
                    try:
                        self._data = tifffile.imread(self.image_filepath)

                    except tifffile.TiffFileError:
                        self._data = np.asarray(Image.open(self.image_filepath))

                self._saved_filepath = None

            self._fix_data_shape_if_needed()
            return self._data

    @data.setter
    def data(self, new_value):
        """
        Allows assignment to the data block (e.g., self.data *= mask)
        """
        with self._lock:
            self.previews = {}
            self._data = new_value
            self._fix_data_shape_if_needed()


    @property
    def shape(self):
        """
        Return the shape of the block.  Tries to avoid loading the image data if possible:
        if we had access to the data block before, we saved the shape into _shape.
        If not, we load the data and get the shape from there.
        """
        with self._lock:
            if self._shape is None:
                self._shape = self.data.shape

            return self._shape

    def index_slices(self, factor=1):
        """
        Return the slices (x_min:x_max, y_min:y_max) needed to insert this block into the BigImage
        with the given factor
        """
        return (
            slice(self.coords[0] // factor, (self.coords[0] + self.shape[0]) // factor),
            slice(self.coords[1] // factor, (self.coords[1] + self.shape[1]) // factor),
        )

    def get_preview(self, factor: int):
        """
        Return a version of the block that is 'factor' smaller.  A factor of 1 is the full-sized original image.
        """
        with self._lock:
            if factor in self.previews:
                return self.previews[factor]

            x, y, c = self.data.shape

            return self.data[0:x:factor, 0:y:factor, :]

    def get_preview_shape(self, factor: int):
        """
        Return the size of the reduced preview using a formula that matches the exact reduction algorithm
        This avoids round off errors when the shape is not a multiple of the reduction factor
        we use the @property shape from EntryBlock because it is cached, and may avoid reading the actual data.
        """
        with self._lock:
            x, y, c = self.shape
            return (len(range(0, x, factor)), len(range(0, y, factor)), c)

    def purge(self, directory):
        """
        Delete from memory the arrays after having saved them in the provided directory.

        """
        with self._lock:
            if not self.is_purged:
                i, j = self.coords
                _saved_filepath = Path(directory, f"Tile@{i}-{j}.npy")
                if not _saved_filepath.exists():
                    np.save(_saved_filepath, self._data)
                    self._saved_filepath = _saved_filepath

                self._data = None
                self.last_access = time.time()

    def cut_block(self, cut_indexes, axis):
        """
        From a list of indexes, cut the image along 'axis' and return the sub blocks as entries.

        This function may not be that useful.  May be removed.
        """
        corrected_indexes = []
        for cut_index in cut_indexes:
            if cut_index < 0:
                corrected_indexes.append(cut_index + self.data.shape[axis])
            else:
                corrected_indexes.append(cut_index)

        split_data = np.split(self.data, corrected_indexes, axis=axis)

        coord_translation = [0]
        coord_translation.extend(corrected_indexes)

        blocks = []
        for i, sub_data in enumerate(split_data):
            translated_coords = list(self.coords)
            translated_coords[axis] += coord_translation[i]

            blocks.append(BlockEntry(coords=translated_coords, data=sub_data))

        return blocks

    def get_overlap_blocks(self, overlap):
        """
        Assuming an overlap of 'overlap' pixels in all directions (top, bottom, left and right),
        cut a block into 9 sub blocks.

        This function may not be that useful.  May be removed.
        """
        entry_strips = self.cut_block(cut_indexes=[overlap, -overlap], axis=0)

        labelled_strips = {
            "-": entry_strips[0],
            "0": entry_strips[1],
            "+": entry_strips[2],
        }

        labelled_entries = {}
        for label, entry_strip in labelled_strips.items():
            strip_cuts = entry_strip.cut_block(cut_indexes=[overlap, -overlap], axis=1)
            labelled_entries[label + "-"] = strip_cuts[0]
            labelled_entries[label + "0"] = strip_cuts[1]
            labelled_entries[label + "+"] = strip_cuts[2]

        return labelled_entries

    @classmethod
    def uniform(cls, shape, value):
        """
        Return a block with a uniform value and a given shape
        """
        block = np.full(shape=shape, fill_value=value)
        return block

    def linear_overlap_mask(self, overlap_in_pixels):
        """
        Calculate the required mask to linearly attenuate the four regions
        of overlap (top, bottom, left and right).
        Notice that the four corners (top-left, top-right bottom-left and bottom-right)
        will be mutiplied twice because they contain both a horizontal mask and a vertical mask.

        This function could be improved with a smoother mask (gaussian, sigmoid, etc)
        """
        mask = np.ones(shape=self.shape, dtype=np.float32)

        individual_masks = self.linear_overlap_masks(overlap_in_pixels)
        for slice_0, slice_1, sub_mask in individual_masks:
            mask[slice_0, slice_1] *= sub_mask

        return mask

    def linear_overlap_masks(self, overlap_in_pixels):
        """
        Calculate the four masks required to linearly attenuate the four regions
        of overlap (top slice, bottom slice, left slice and right slice).
        Notice that the four corners (top-left, top-right bottom-left and bottom-right)
        will be mutiplied twice because they contain both a horizontal mask and a vertical mask.
        """
        if (
            overlap_in_pixels > self.shape[0] / 2
            or overlap_in_pixels > self.shape[1] / 2
        ):
            raise ValueError("Overlap cannot be larger than half the size of the block")

        x,y,channels = self.shape

        mask_low0 = np.ones(shape=(overlap_in_pixels, y, channels), dtype=np.float32)
        mask_high0 = np.ones(shape=(overlap_in_pixels, y, channels), dtype=np.float32)
        mask_low1 = np.ones(shape=(x, overlap_in_pixels, channels), dtype=np.float32)
        mask_high1 = np.ones(shape=(x, overlap_in_pixels, channels), dtype=np.float32)

        zero_to_one = np.array(np.linspace(0, 1, overlap_in_pixels), dtype=np.float32)
        one_to_zero = np.array(np.linspace(1, 0, overlap_in_pixels), dtype=np.float32)

        for c in range(channels):
            for k in range(y):
                mask_low0[:, k, c] *= zero_to_one
                mask_high0[:, k, c] *= one_to_zero

            for k in range(x):
                mask_low1[k, :, c] *= zero_to_one
                mask_high1[k, :, c] *= one_to_zero

        return [
            (slice(0, overlap_in_pixels), slice(0, y), mask_low0),
            (range(-overlap_in_pixels, 0, 1), slice(0, y), mask_high0),
            (slice(0, x), slice(0, overlap_in_pixels), mask_low1),
            (slice(0, x), range(-overlap_in_pixels, 0, 1), mask_high1),
        ]

    def apply_mask(self, mask):
        """
        Multiplies the data block by a mask of the same size.  The multiplication is upgraded
        to the dtype of the mask, then cast back to the original type of the data. If the mask makes the data
        go over the maximum range of the original type, it will roll over.
        """
        self.data = np.multiply(self.data, mask).astype(self.data.dtype)

    def apply_partial_masks(self, masks_with_slices):
        """
        Go through the list and apply all masks
        """
        for slice_0, slice_1, mask in masks_with_slices:
            self.apply_partial_mask(slice_0, slice_1, mask)

    def apply_partial_mask(self, slice_0, slice_1, mask):
        """
        Multiplies the data block by a mask of a smaller size.  The multiplication is upgraded
        to the dtype of the mask, then cast back to the original type of the data.
        """
        self.data[slice_0, slice_1] = np.multiply(
            self.data[slice_0, slice_1,:], mask
        ).astype(self.data.dtype)


class BigImage:
    """
    A class for extremely large images that manages memory efficiently to preview a lower resolution version quickly
    """

    def __init__(self, size=None):
        """
        Create BigImage with an expected size. If the size is None, it will be computed
        from the entries when needed in get_preview.  If the provided size is too small
        to accomodate all the images, an error will occur.
        """
        self.size = size
        self.data = None
        self.other_resolutions = []
        self.entries = []
        self._work_dir = (
            tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        )

    def __del__(self):
        """
        To avoid warnings, we explicitly cleanup the temporary directory
        """
        self._work_dir.cleanup()

    def add_block(self, coords, data=None, image_filepath=None):
        """
        The data from the numpy array 'data' goes to pixel "coords" in the large image

        BlockEntries are kept in a simple list that is used to reconstruct the low resolution version
        """
        if data is None and image_filepath is None:
            raise ValueError("You must provide either the numpy data or an image file")

        self.entries.append(
            BlockEntry(coords=coords, data=data, image_filepath=image_filepath)
        )

    def add_entry(self, entry):
        """
        Adds an entry to the entries.  It could be an already-loaded image or a filepath, we do not
        concern ourselves with the details.
        """
        self.entries.append(entry)

    def purge_if_needed(self):
        """
        Purges if process memory is getting too large
        """
        process = psutil.Process()
        memory_used_by_process_in_gb = process.memory_info().rss
        memory_available_in_gb = psutil.virtual_memory().available
        total_memory = memory_used_by_process_in_gb + memory_available_in_gb
        if memory_used_by_process_in_gb / total_memory > 0.9:
            self.purge()

    def purge(self):
        """
        Purges arrays from memory and save everything to disk
        """
        for entry in self.entries:
            entry.purge(directory=self._work_dir.name)

    def calculate_size(self, factor=1):
        """
        Calculate the size of the image considering the tiles present with a reduction factor
        """
        max_x = 0
        max_y = 0
        small_shape = None
        for entry in self.entries:
            small_shape = entry.get_preview_shape(factor=factor)
            max_x = max(entry.coords[0] // factor + small_shape[0], max_x)
            max_y = max(entry.coords[1] // factor + small_shape[1], max_y)
        return max_x, max_y, small_shape[2]

    def get_reduced_resolution_preview(self, factor=16, progress=None):
        """
        Put together all blocks in a reduced version of the final image, reduced
        by a a value of "factor" (i.e. factor 2 is half the size, 1 is the original size)
        Nothing fancy for overlap: just overwrite the data. If a size
        was provided, it must be large enough to contain the blocks
        """

        small_width, small_height, channels = self.calculate_size(factor)

        preview = None

        if progress is None:
            progress = Progress(total=len(self.entries), delay_before_showing=1)

        with progress as p:
            for entry in self.entries:
                small_block = entry.get_preview(factor=factor)
                scaled_x, scaled_y = (
                    entry.coords[0] // factor,
                    entry.coords[1] // factor,
                )

                slice0 = slice(scaled_x, scaled_x + small_block.shape[0])
                slice1 = slice(scaled_y, scaled_y + small_block.shape[1])

                if preview is None:
                    preview = np.zeros(
                        shape=(small_width, small_height, channels), dtype=small_block.dtype
                    )

                preview[slice0, slice1,:] += small_block
                self.purge_if_needed()
                p.next()

        return preview

    def get_reduced_resolution_block(self, coords, factor=1):
        """
        Get a reduced preview for a block at given coordinates if available
        """
        for entry in self.entries:
            if entry.coords == coords:
                return entry.get_preview(factor)
        return None
