from caproto import ChannelData, ChannelType
from caproto.server import (PVGroup, SubGroup, pvproperty, PvpropertyString,
                            PvpropertyInteger)


#@define
class Analysis(PVGroup):
    """
    A group of PVs providing the analysis of an image. 
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
    total_counts = pvproperty(value=0.0, name = "total_counts", doc="total intensity")
    center_of_mass_row = pvproperty(value=0.0, name = "center_of_mass_row", doc="center of mass in units of pixel")
    center_of_mass_col = pvproperty(value=0.0, name = "center_of_mass_col", doc="center of mass in units of pixel")

