# BliqTools
Cross-platform Python tools to manipulate any type of images and data from Bliq microscopes (and general).  Used by Bliq programmers internally and by the community.
For now, fairly limited with only tools for unittesting and limited tools for nirvana files and folders, but the goal is to add more and more this project public.

# Project objectives
1. To collect often-used tools in a single package, easy to install.
2. To make manipulation of images task-oriented by removing the boiler-plate, generic code.
3. To let the community look at the code, and tailor it to their needs.

# Installing

Python 3.12 is the version used for development, and setuptools have evolved away from `setup.py`. The best method to install `bliqtools` is `pip`:

```shell
pip install bliqtools
```

or install from source:

```shell
cd bliqtools/ # In root directory of project prproject.toml
python3 -m pip install .
```

This will install with the current version of Python. You can then use it in scripts with:

```python
from bliqtools.testing import MemoryMonitor, Progress, TimeIt, Debuggable
from bliqtools.nirvana import FilePath
from bliqtools.bigimage import BigImage
```

# Tools for managing metadata in Nirvana filenames 
A very simple extension to `pathlib.Path`: an extension that will automatically extract all the metadata from the filename as described in Nirvana's software.
This metadata is then available using properties.  See the unittests at the end of the `nirvana.py` file.

# Tools for very large images: `BigImage` previews

A class called `BigImage` is available to construct a very large image with small blocks.  The class will manage any memory issues and will save to disk the data if needed.  The main method is `get_preview(factor)` that provides a scaled down version for display. The construction of this preview is very fast (less than a second for a 1 GB image from 17x17 data blocks of size 2048x2048).

## Example usage
```python
from bliqtools.bigimage import BigImage

img = BigImage()
for i in range(10):
    for j in range(10):
        small_block = np.random.randint(
            0, 255, size=(2048, 2048), dtype=np.uint8
        )
        img.add_block(coords=(i * 2048, j * 2048), data=small_block)

preview = img.get_reduced_resolution_preview(factor=32)
plt.imshow(preview)
plt.show()
```


# Tools for unittesting

In `bliqtools.testing`, you will find these functions. You can also run the tests that are incorporated directly into the file by running it.

1. `Progress` is a simple class used with contextlib that can provide reasonable feedback.  The user provides total number of iterations and calls next() every iterations.
```python
        with Progress(self.total, description="Volume creation") as progress:
            for i,j,k in self.index_list:
                tile = self.tile(i,j,k)
                volume[i-1,j-1,k-1,:,:] = tile
                progress.next()
```

2. `TimeIt` is a simple class to time a small section of code:

```python
        with TimeIt(f"Get layers (single)"):
            stitcher.get_layers()
```

3. `Debuggable` can be used as a parent class to get useful debugging functions, like _dump_internals() or to see what variables have changed between calls.

```python
    def test_base_stitcher_still_working(self):
        stitcher = Stitcher(self.valid_root_dir, overlap=0.2, channel="Grayscale")
        self.assertIsNotNone(stitcher)
        # stitcher._save_state()
        stitcher.array_from_tiff_dirs()
        stitcher.make_z_stack()
        stitcher._dump_internals()
```

will print:

```
-- begin test_base_stitcher_still_working (/Users/dccote/GitHub/Stitching/stitcher.py @line 276)

   no_c_directory [<class 'str'>                           ] : /Users/dccote/Downloads/Test_maps
   app_directory  [<class 'NoneType'>                      ] : None
   overlap        [<class 'float'>                         ] : 0.2
   dtype          [<class 'numpy.dtypes.UInt8DType'>       ] : uint8
   channel        [<class 'str'>                           ] : Grayscale
   channels       [<class 'NoneType'>                      ] : None
   start_memory   [<class 'int'>                           ] : 8276803584
   save_name      [<class 'NoneType'>                      ] : None
   array_paths    [<class 'list'>                          ] : []
   sorted_files   [<class 'list'>                          ] : len=945
   use_zarr_arrays[<class 'bool'>                          ] : False
   og_arrays      [<class 'NoneType'>                      ] : None
   z_stacks       [<class 'numpy.ndarray'>                 ] : shape=(5, 740, 2780)

-- end test_base_stitcher_still_working (/Users/dccote/GitHub/Stitching/stitcher.py @line 276)
```


4. `MemoryMonitor` can monitor memory in a separate thread during a long calculation to provide insight on performance.  It will print out the time and memory available when done:

```python
        with MemoryMonitor(self.id()) as monitor:
            stitcher = ArrayStitcher(volume_kji=volume)
            with TimeIt(f"Save Zarr {volume_shape}"):
                stitcher.save("/tmp/test-zarr.tif")

```
and can be used to provide a graph of memory available vs time:

<img width="757" alt="image" src="https://github.com/user-attachments/assets/231d13d6-5202-45c8-8855-4c42bcc0c55e">

