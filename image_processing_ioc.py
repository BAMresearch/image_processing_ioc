
import logging
import socket
import sys
from typing import Union
import attrs
from datetime import datetime, timezone
from caproto.server import PVGroup, SubGroup, pvproperty, PvpropertyString, run, template_arg_parser, AsyncLibraryLayer
from pathlib import Path
import logging
from analysis import Analysis
import hdf5plugin
import h5py
import numpy as np
from skimage.measure import regionprops


logger = logging.getLogger("image_processing_ioc")
logger.setLevel(logging.INFO)

def hdf5_get_image(filename:Path, h5imagepath: str = "entry/data/data") -> np.ndarray:
    with h5py.File(filename, 'r') as h5f:
        image = h5f[h5imagepath][()]
    return image

def beam_analysis(imageData: np.ndarray, ROI_SIZE: int) -> Union[tuple, float]:
    """
    Perform beam analysis on the given image data, returning the beam center and flux.
    """
    # Step 1: reducing the dimensionality of the imageData by averaging until we have a 2D array:
    while imageData.ndim > 2:
        imageData = np.mean(imageData, axis=0)

    # Step 2: get rid of masked or pegged pixels on an Eiger detector
    labeled_foreground = (np.logical_and(imageData >= 0, imageData <= 1e6)).astype(int)
    maskedTwoDImage = imageData * labeled_foreground  # apply mask
    threshold_value = np.maximum(
        1, 0.0001 * maskedTwoDImage.max()
    )  # filters.threshold_otsu(maskedTwoDImage) # ignore zero pixels
    labeled_peak = (maskedTwoDImage > threshold_value).astype(int)  # label peak
    properties = regionprops(labeled_peak, imageData)  # calculate region properties
    center_of_mass = properties[0].centroid  # center of mass (unweighted by intensity)
    weighted_center_of_mass = properties[
        0
    ].weighted_centroid  # center of mass (weighted)
    # determine the total intensity in the region of interest, this will be later divided by measuremet time to get the flux
    ITotal_region = np.sum(
        maskedTwoDImage[
            np.maximum(int(weighted_center_of_mass[0] - ROI_SIZE), 0) : np.minimum(
                int(weighted_center_of_mass[0] + ROI_SIZE), maskedTwoDImage.shape[0]
            ),
            np.maximum(int(weighted_center_of_mass[1] - ROI_SIZE), 0) : np.minimum(
                int(weighted_center_of_mass[1] + ROI_SIZE), maskedTwoDImage.shape[1]
            ),
        ]
    )
    # for your info:
    logging.debug(f"{center_of_mass=}")
    logging.debug(f"{ITotal_region=} counts")

    return center_of_mass, ITotal_region



# @attrs.define
class ImageProcessingIOC(PVGroup):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    ImagePathPrimary = pvproperty(value = "", name="ImagePathPrimary", doc="Path to the first image (e.g. a direct beam image)", string_encoding='utf-8', report_as_string=True, max_length=255)
    ImagePathSecondary = pvproperty(value = "", name="ImagePathSecondary", doc="Path to the second image (e.g. direct beam through sample)", string_encoding='utf-8', report_as_string=True, max_length=255)
    ROI_rowmin = pvproperty(value = 0, name="ROI_rowmin", doc="Minimum row of the region of interest")
    ROI_rowmax = pvproperty(value = 1065, name="ROI_rowmax", doc="Maximum row of the region of interest")
    ROI_colmin = pvproperty(value = 0, name="ROI_colmin", doc="Minimum column of the region of interest")
    ROI_colmax = pvproperty(value = 1030, name="ROI_colmax", doc="Maximum column of the region of interest")
    ROI_size = pvproperty(value = 25, name="ROI_size", doc="Size of the region of interest around the beam used by beamanalysis")
    primary = SubGroup(Analysis, prefix="primary:")
    secondary = SubGroup(Analysis, prefix="secondary:")
    ratio = pvproperty(value = 0.0, name="ratio", doc = "ratio of the secondary / primary beam intensities")

    async def compute_ratio(self):
        if self.primary.total_counts.value > 0 and self.secondary.total_counts.value > 0:
            await self.ratio.write(self.secondary.total_counts.value / self.primary.total_counts.value)

    @ImagePathPrimary.putter
    async def ImagePathPrimary(self, instance, value: str):
        if not Path(value).is_file():
            # do nothing
            logger.warning(f"File {value} does not exist")
            return 

        image = hdf5_get_image(Path(value))
        image_clipped = image[
            np.maximum(self.ROI_rowmin, 0):np.minimum(self.ROI_rowmax, image.shape[0]),
            np.maximum(self.ROI_colmin, 0):np.minimum(self.ROI_colmax, image.shape[1])
            ]
        COM, Itotal = beam_analysis(image_clipped, self.ROI_size)
        await self.primary.total_counts.write(Itotal)
        await self.primary.center_of_mass_row.write(COM[0])
        await self.primary.center_of_mass_col.write(COM[1])
        await self.compute_ratio()
        
    @ImagePathSecondary.putter
    async def ImagePathSecondary(self, instance, value: str):
        if not Path(value).is_file():
            # do nothing
            logger.warning(f"File {value} does not exist")
            return

        image = hdf5_get_image(Path(value))
        image_clipped = image[
            np.maximum(self.ROI_rowmin, 0):np.minimum(self.ROI_rowmax, image.shape[0]),
            np.maximum(self.ROI_colmin, 0):np.minimum(self.ROI_colmax, image.shape[1])
            ]
        COM, Itotal = beam_analysis(image_clipped, self.ROI_size)
        await self.secondary.total_counts.write(Itotal)
        await self.secondary.center_of_mass_row.write(COM[0])
        await self.secondary.center_of_mass_col.write(COM[1])
        await self.compute_ratio()



def main(args=None):
    parser, split_args = template_arg_parser(
        default_prefix="Portenta:",
        desc="EPICS IOC for analysing detector images",
    )

    if args is None:
        args = sys.argv[1:]

    args = parser.parse_args()

    logging.info("Running Networked Portenta IOC")

    ioc_options, run_options = split_args(args)
    ioc = ImageProcessingIOC(**ioc_options)
    run(ioc.pvdb, **run_options)


if __name__ == "__main__":
    main()
