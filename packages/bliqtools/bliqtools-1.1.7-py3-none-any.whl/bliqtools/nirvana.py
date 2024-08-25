"""
This module is a helper to access files as saved by Nirvana VMS and Lightsheet
from Bliq Photonics.

You can do:
    
    import bliqtools.nirvana

"""

import os
import re
from enum import StrEnum
from pathlib import Path
import subprocess
from contextlib import redirect_stderr

from pyometiff import OMETIFFReader, OMEXML


class FileType(StrEnum):
    """
    The types of files produced and recognized by Nirvana
    """

    IMAGE_VMS = "ImageVMS"
    IMAGE_TILE = "ImageTile"
    # Not ready yet
    # IMAGE_LIGHTSHEET = "ImageLightsheet"
    # IMAGE_SPARQ_HI = "ImageSparqHi"
    # IMAGE_SPARQ_LO = "ImageSparqLo"
    # IMAGE_SLAM = "ImageSlam"

    DIRECTORY = "Directory"
    SYSTEM_FILE = "System file"
    UNKNOWN = "Unknown"


class FilePath(Path):
    """
    An extension to the Path class of PathLib to include metadata obtained from the filename itself
    """

    patterns = {
        FileType.IMAGE_VMS: {
            "regex": r"-([^-.]+?)-Ch-(\d)-Frame_(\d+)-Time_(\d.+?)s",
            "groups": ["provider", "channel", "frame", "time"],
            "types": [str, int, int, float],
        },
        FileType.IMAGE_TILE: {
            "regex": r"VOI.(\d+).X(\d+?).Y(\d+?).Z(\d+?).C(\d+).T(\d+)",
            "groups": ["voi", "i", "j", "k", "channel", "time"],
            "types": [int, int, int, int, int, int],
        },
        FileType.SYSTEM_FILE: {
            "regex": r"^\..+",
            "groups": [],
            "types": [],
        },
    }

    registered_metadata = [
        "provider",
        "channel",
        "frame",
        "time",
        "filetype",
        "i",
        "j",
        "k",
        "voi",
    ]

    def __init__(self, *args):
        """
        Initializing file from complete filepath
        """
        super().__init__(*args)

        self.metadata = self.extract_metadata()

    def __getattribute__(self, name):
        if name in FilePath.registered_metadata:
            return self.metadata.get(name, None)

        return super().__getattribute__(name)

    @classmethod
    def is_nirvana_filetype(cls, filepath):
        """
        Returns if a name is a valid Nirvana file name before creating an object File
        """
        metadata = FilePath(filepath).metadata

        if metadata["filetype"] != FileType.UNKNOWN:
            return True

        return False

    @property
    def ome_tiff(self):
        """
        Returns a dictionary containing the OME-TIFF metadata
        """
        return self.metadata.get("ome-tiff", None)

    @property
    def ome_xml(self):
        """
        Return an object to access the OME-XML properties. To obtain the text, use self.metadata['ome-xml']
        See documentation at https://github.com/filippocastelli/pyometiff/blob/main/pyometiff/omexml.py
        """
        ome_xml = self.metadata.get("ome-xml", None)
        if ome_xml is not None:
            return OMEXML(ome_xml)
        return None

    def extract_metadata(self):
        """
        Extract all metadata available (from filename, and OME TIFF)
        """
        metadata = {}

        filename_metadata = self.extract_filename_metadata()

        metadata.update(filename_metadata)

        filetype = filename_metadata["filetype"]
        if filetype in [FileType.IMAGE_VMS, FileType.IMAGE_TILE]:
            ome_metadata, xml_metadata = self.extract_ome_metadata()

            if ome_metadata is not None:
                metadata["ome-tiff"] = ome_metadata
            if xml_metadata is not None:
                metadata["ome-xml"] = xml_metadata

        return metadata

    def extract_filename_metadata(self):
        """
        Extract metadata from filename
        """

        filepath = self

        metadata = {"filetype": FileType.UNKNOWN, "filepath": str(filepath)}
        if Path(filepath).is_dir():
            metadata["filetype"] = FileType.DIRECTORY

        filename = Path(filepath).name
        for filetype, matching_info in self.patterns.items():
            match = re.search(matching_info["regex"], filename)
            if match is not None:
                for i, name in enumerate(matching_info["groups"]):
                    cast_type = matching_info["types"][i]
                    metadata[name] = cast_type(match.group(i + 1))
                metadata["filetype"] = filetype

        return metadata

    def extract_ome_metadata(self):
        """
        Extract OME metadata from TIFF file when available
        """

        if self.exists():
            with redirect_stderr(
                None
            ):  # Suppress the stderr when OME metadata not available
                reader = OMETIFFReader(fpath=self)
                _, metadata, xml_metadata = reader.read()
                return metadata, xml_metadata
        else:
            return None, None

    def write_xattr(self, prefix="bliq.nirvana"):
        """
        On macOS (Darwin) and Linux, extended attributes are available in the file system
        We write our metadata extracted from the filename to the extended attribute of the file
        By default, the prefix "bliq.nirvana" is added to the metadata property.
        """
        for key, value in self.metadata.items():
            if key != "filepath":
                job = subprocess.run(
                    ["xattr", "-w", f"{prefix}.{key}", f"{value}", str(self)],
                    check=True,
                )
                if job.returncode != 0:
                    raise RuntimeError(
                        f"Unable to set extended attributes for file {self}"
                    )

    def delete_xattr(self, prefix="bliq.nirvana"):
        """
        On macOS (Darwin) and Linux, extended attributes are available in the file system
        We delete our metadata previoulsy written to the extended attribute of the file
        By default, the prefix "bliq.nirvana" is added to the metadata property.
        """
        for key, _ in self.metadata.items():
            if key != "filepath":
                job = subprocess.run(
                    ["xattr", "-d", f"{prefix}.{key}", str(self)], check=True
                )
                if job.returncode != 0:
                    raise RuntimeError(
                        f"Unable to delete extended attributes for file {self}"
                    )

    def contents(self, ignore_system_files=True):
        """
        Returns the content of a directory as a list of FilePath objects
        By default, will ignore system files (defined as beginning with a dot)
        """
        filepaths = []
        for filename in os.listdir(self):
            filepath = FilePath(self, filename)
            if not ignore_system_files or filepath.filetype != FileType.SYSTEM_FILE:
                filepaths.append(filepath)

        return filepaths
