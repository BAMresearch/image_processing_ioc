# image_processing_ioc
IOC that takes one or two files and exposes image analysis results. 

## Usage

### Server

To start the IOC use:

```sh
 python image_processing_ioc.py --prefix image: --list-pvs
```

This makes the following EPICS PVs available:

```sh
    image:ImagePathPrimary
    image:ImagePathSecondary
    image:ROI_rowmin
    image:ROI_rowmax
    image:ROI_colmin
    image:ROI_colmax
    image:ROI_size
    image:primary:total_counts
    image:primary:center_of_mass_row
    image:primary:center_of_mass_col
    image:secondary:total_counts
    image:secondary:center_of_mass_row
    image:secondary:center_of_mass_col
    image:ratio
```

### Client

To set new file paths use either:

```sh
caproto-put image:ImagePathPrimary '"/path/to/file/eiger_0051112_data_000001.h5"'
```
with double quotes around the path.

Alternatively, in python:
```python
import caproto.threading.pyepics_compat as epics

epics.caput('image:ImagePathPrimary', "/path/to/file/eiger_0051112_data_000001.h5")

```
The path is not parsed correctly if `caput` from `pyepics` is used instead.
