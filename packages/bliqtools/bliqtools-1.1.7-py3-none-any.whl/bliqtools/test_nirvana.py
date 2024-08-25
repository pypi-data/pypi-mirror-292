"""
Unit tests for Nirvava FilePath class
"""
import envtest
import unittest
from pathlib import Path
from bliqtools.nirvana import FileType, FilePath, OMEXML


class TestClasses(unittest.TestCase):
    """
    Unittesting demonstrating use of classes.

    """

    test_dir = Path(Path(__file__).parent, "test_data")
    filepath = Path(
        test_dir,
        "Test-001",
        "FLIR camera-Ch-1",
        "Test-001-FLIR camera-Ch-1-Frame_002377-Time_0.023s.tif",
    )
    large_FilePath = ""
    nirvana_dir = Path(test_dir, "Test-001")
    channel_dir = Path(test_dir, "Test-001", "FLIR camera-Ch-1")

    def short_test_id(self):
        """
        Simple function to identify running test
        """
        return self.id().split(".")[
            -1
        ]  # Remove complete class name before the function name

    def test_check_metadata(self):
        """
        Extract metadata from filename
        """
        nirvana_file = FilePath(self.filepath)
        self.assertIsNotNone(nirvana_file)
        metadata = nirvana_file.metadata
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["provider"], "FLIR camera")
        self.assertEqual(metadata["channel"], 1)
        self.assertEqual(metadata["frame"], 2377)
        self.assertEqual(metadata["time"], 0.023)
        self.assertEqual(metadata["filetype"], FileType.IMAGE_VMS)

    def test_get_metadata_as_properties(self):
        """
        Meta data properties are accessible as Python properties
        """
        nirvana_file = FilePath(self.filepath)
        self.assertIsNotNone(nirvana_file)
        self.assertEqual(nirvana_file.provider, "FLIR camera")
        self.assertEqual(nirvana_file.channel, 1)
        self.assertEqual(nirvana_file.frame, 2377)
        self.assertEqual(nirvana_file.time, 0.023)
        self.assertEqual(nirvana_file.filetype, FileType.IMAGE_VMS)

    def test_init_valid_nirvana_filepath(self):
        """
        The FilePath must exist and be a directory
        """
        f = FilePath("/tmp")
        self.assertIsNotNone(f)

    def test_get_files(self):
        """
        The FilePath must contain Nirvana files with understandable metadata
        """

        f = FilePath(self.channel_dir)
        self.assertIsNotNone(f)
        files = f.contents()
        self.assertIsNotNone(files)
        self.assertTrue(len(files) == 3)

    def test_get_all_metadata_from_filepath(self):
        """
        We can obtain a list of metadata for each file, and it must include filepath
        """
        f = FilePath(self.channel_dir)
        metadata = [filepath.metadata for filepath in f.contents()]
        self.assertEqual(len(metadata), 3)
        self.assertIsNotNone(metadata[0]["filepath"])

    def test_is_a_nirvana_file(self):
        """
        Check if name is valid before creating object
        """
        self.assertTrue(FilePath.is_nirvana_filetype(self.filepath))
        self.assertFalse(FilePath.is_nirvana_filetype("/tmp/123.tif"))

    @unittest.skip("No access")
    def test_large_filepath(self):
        """
        Retrieve large number of files from directory (only tested locally)
        """
        f = FilePath(self.large_FilePath)
        self.assertIsNotNone(f)
        files = f.get_nirvana_files()
        self.assertTrue(len(files) > 60_000)

    def test_is_file(self):
        """
        We can still use the functions of the parent Path. Check that it is a file
        """
        nirvana_file = FilePath(self.filepath)
        self.assertTrue(nirvana_file.is_file())

    def test_is_dir(self):
        """
        We can still use the functions of the parent Path. Check that it is a directory
        """
        nirvana_file = FilePath(self.test_dir)
        self.assertTrue(nirvana_file.is_dir())

    def test_dir_content(self):
        """
        We can obtain the contents of a directory as an array of FilePaths
        """
        nirvana_file = FilePath(self.test_dir, "Test-001", "FLIR camera-Ch-1")

        images = [
            filepath
            for filepath in nirvana_file.contents()
            if filepath.filetype == FileType.IMAGE_VMS
        ]
        self.assertEqual(len(images), 3)

    def test_filetypes(self):
        """
        Each FileType is recognized from a regular expression of the filename.
        """
        self.assertEqual(
            FilePath(
                "test_data/Test-001-FLIR camera-Ch-1-Frame_002377-Time_0.023s.tif"
            ).filetype,
            FileType.IMAGE_VMS,
        )
        self.assertEqual(
            FilePath("test_data/Test-001-VOI_1_X001_Y002_Z003_C1-T0.tif").filetype,
            FileType.IMAGE_TILE,
        )
        self.assertEqual(
            FilePath(self.test_dir, ".DS_Store").filetype, FileType.SYSTEM_FILE
        )
        self.assertEqual(FilePath(self.test_dir).filetype, FileType.DIRECTORY)
        self.assertEqual(FilePath("whatever").filetype, FileType.UNKNOWN)

    def test_write_xattr(self):
        """
        Test that we can write the metadata as extended attributes of a file
        """
        f = FilePath(
            self.test_dir,
            "Test-001/FLIR camera-Ch-1/Test-001-FLIR camera-Ch-1-Frame_002377-Time_0.023s.tif",
        )
        self.assertTrue(f.exists())
        f.write_xattr()

    def test_write_delete_xattr(self):
        """
        Test that we can delete the metadata as extended attributes of a file
        """
        f = FilePath(
            self.test_dir,
            "Test-001/FLIR camera-Ch-1/Test-001-FLIR camera-Ch-1-Frame_002379-Time_0.067s.tif",
        )
        self.assertTrue(f.exists())
        f.write_xattr()
        f.delete_xattr()

    def test_ome_metadata(self):
        """
        Test showing that we can extract OME metadata from TIFF files
        """
        f = FilePath(self.test_dir, "image-008-VOI_1-X001-Y001-Z001-C1-T001.tif")
        ome_metadata, xml_metadata = f.extract_ome_metadata()
        self.assertIsNotNone(ome_metadata)
        self.assertTrue(type(ome_metadata), dict)
        self.assertTrue(len(ome_metadata) > 0)
        self.assertIsNotNone(xml_metadata)
        self.assertTrue(type(xml_metadata), str)
        self.assertTrue(len(xml_metadata) > 0)

    def test_ome_tiff_properties_metadata(self):
        """
        Test showing that we can extract OME metadata from TIFF files
        """
        f = FilePath(self.test_dir, "image-008-VOI_1-X001-Y001-Z001-C1-T001.tif")
        self.assertIsNotNone(f.ome_tiff)
        self.assertTrue(isinstance(f.ome_tiff, dict))
        self.assertIsNotNone(f.ome_xml)
        self.assertTrue(isinstance(f.ome_xml, OMEXML))
        self.assertIsNotNone(f.metadata["ome-xml"])
        self.assertTrue(isinstance(f.metadata["ome-xml"], str))

    def test_ome_xml_metadata(self):
        """
        Explore the OME-XML data provided with OMEXML
        See documentation at https://github.com/filippocastelli/pyometiff/blob/main/pyometiff/omexml.py
        """
        f = FilePath(self.test_dir, "image-008-VOI_1-X001-Y001-Z001-C1-T001.tif")
        _, xml_metadata = f.extract_ome_metadata()
        obj = OMEXML(xml_metadata)
        self.assertTrue(isinstance(xml_metadata, str))
        self.assertFalse(isinstance(obj, str))
        self.assertEqual(obj.image().Pixels.channel_count, 1)


if __name__ == "__main__":
    unittest.main()
