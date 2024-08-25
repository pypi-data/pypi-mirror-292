
import sys
import os
from pathlib import Path

directory = Path(os.path.dirname(os.path.abspath(__file__)))
module_dir = directory.parts[0:directory.parts.index('bliqtools')+1]

sys.path.insert(
    0, str(Path(*module_dir))
)

import unittest
import shutil
from contextlib import suppress

import numpy as np
import tifffile
from matplotlib import pyplot as plt

from bliqtools.testing import MemoryMonitor, TimeIt, Progress



class TestCaseBigImage(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    Several methods to create datasets and organize tests for BigImage
    """

    img_graph_path = None
    img_test_data = None

    @classmethod
    def setUpClass(cls):
        cls.img_graph_path = "/tmp/Graphs"
        shutil.rmtree(cls.img_graph_path, ignore_errors=True)
        Path(cls.img_graph_path).mkdir(parents=True, exist_ok=True)

        cls.img_test_data = Path("/tmp/Test_Data")
        cls.dataset_grayscale = Path(cls.img_test_data, "grayscale")
        cls.dataset_rgb = Path(cls.img_test_data, "rgb")
        
        shutil.rmtree(cls.img_test_data, ignore_errors=True)
        cls.dataset_grayscale.mkdir(parents=True, exist_ok=True)
        cls.dataset_rgb.mkdir(parents=True, exist_ok=True)

        cls.create_dataset()

    @classmethod
    def tearDownClass(cls):
        """
        We save the graphs into files to avoid blocking the UI.  Open the folder when done (macOS)
        """
        with suppress(Exception):
            subprocess.run(["open", cls.img_graph_path], check=True)

        shutil.rmtree(cls.img_test_data, ignore_errors=True)

    @classmethod
    def create_dataset(cls):
        map_size = (10, 10, 4)
        shape_rgb = (512, 512, 3)
        shape_grayscale = (512, 512)
        overlap = 50

        with MemoryMonitor():
            with Progress(total=map_size[0] * map_size[1], description="Tile") as p:
                for i in range(map_size[0]):
                    for j in range(map_size[1]):
                        for k in range(map_size[2]):
                            block = np.full(
                                shape=shape_rgb, fill_value=10 * i + 100 * j, dtype=np.uint8
                            )
                            # We follow Nirvana's naming conventions (see nirvana.py)
                            filepath = Path(cls.dataset_rgb, "test_rgb_TEST-VOI_001-X{0:03}-Y{1:03}-Z{2:03}-C1-T001.tif".format(i+1,j+1,k+1))
                            tifffile.imwrite(filepath, block)

                            block = np.full(
                                shape=shape_grayscale, fill_value=10 * i + 100 * j, dtype=np.uint8
                            )
                            # We follow Nirvana's naming conventions (see nirvana.py)
                            filepath = Path(cls.dataset_grayscale, "test_grayscale_TEST-VOI_001-X{0:03}-Y{1:03}-Z{2:03}-C1-T001.tif".format(i+1,j+1,k+1))
                            tifffile.imwrite(filepath, block)

    def current_test_name(self):
        """
        A short name that identifies a test for titles on figures and filenames
        """
        return self.id().split(".")[-1]

    def save_test_image_result(self, img, suffix=""):
        plt.imshow(img, interpolation="nearest")
        plt.title(self.current_test_name())
        image_path = Path(self.img_graph_path, self.current_test_name() + f"{suffix}.pdf")
        plt.savefig(image_path)


if __name__ == "__main__":
    print(sys.path)