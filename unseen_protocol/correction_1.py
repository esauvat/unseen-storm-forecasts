# 
# Apply the first correction to the unseen protocol.
# It will correct the data by adjusting the mean of the 
# modelled distributions to the mean of the observed distribution.
#

from sys import argv
import xarray as xr
import numpy as np

from numpy.typing import NDArray



#
#       Correction array
#

corrections = np.array([
    0,      # Index adjusting
    0,      # January
    0,      # February
    0,      # March
    0,      # April
    4.5,    # May
    7,      # June
    10,     # July
    9.5,    # August
    8,      # September
    3,      # October
    0,      # November
    0,      # December
])



#
#       Function
#

def main(
        ds: xr,
        shift: NDArray,
) -> xr.Dataset:
    """
    Add the wanted corretion to the data.

    Parameters:
        ds : Processed data
        shift : Array of bias corrections for each month

    Returns:
        Corrected data
    """

    addVals: NDArray = shift[
        ds['month'].values
    ]

    ds['tp24'].values += addVals

    return ds


#
#       Running script
#

if __name__ == "__main__":

    if len(argv) >= 2 and argv[1] == "forecast":
        selector = "forecast"
    elif len(argv) >= 2 and argv[1] == "hindcast":
        selector = "hindcast"
    else:
        selector = "full"

    data = xr.open_dataset("data/processed-"+selector+".nc")

    res = main(data, corrections)
    res.to_netcdf("data/corrected-"+selector+".nc")