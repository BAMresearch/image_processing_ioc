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
    image:ImagePathPrimary             - input: file path to a detector image
    image:ImagePathSecondary           - input: file path to a detector image
    image:ROI_rowmin                   - input: rough ROI for isolating the likely area to find the beam in
    image:ROI_rowmax                   - input
    image:ROI_colmin                   - input
    image:ROI_colmax                   - input
    image:ROI_size                     - input: pixel number (e.g. 25), fine-tunes the area around the found direct beam for determining peak properties
    image:primary:total_counts         - output: total counts in the fine-tuned ROI
    image:primary:center_of_mass_row   - output: the COM of the found beam in float pixels
    image:primary:center_of_mass_col   - output
    image:secondary:total_counts       - output
    image:secondary:center_of_mass_row - output
    image:secondary:center_of_mass_col - output
    image:ratio                        - output: ratio between the total counts of secondary / primary
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
