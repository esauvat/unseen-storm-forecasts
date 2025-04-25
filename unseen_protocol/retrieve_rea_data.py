#
# Retrieve the reanalysis data and store it into a single DataArray to grand quicker access.
#
# This reanalysis data will be used to assess the fidelity of the s2s model.
#

import xarray as xr
import numpy as np
import pickle

from weatherdata.classes import Weatherset
from weatherdata.geographics import apply_curv_weights
from weatherdata import mean_over_time



###############################################################
#
#       Functions
#

def process_file(
        arr: xr.DataArray,
) -> xr.DataArray:
    """
    Select the wanted data in the reanalysis files, not applying the mean
    """

    da: xr.DataArray = arr.sel(
        latitude = slice(62.5, 60.5),
        longitude = slice(9,11.75)
    )
    return apply_curv_weights(
            da
    ).mean(
        dim=["latitude", "longitude"]
    )

def main() -> xr.DataArray:
    """
    Compute a DataArray with all the data and apply the mean over time
    """

    da_res: xr.DataArray = None

    toProcessQueue: list[tuple] = [key for key in tpSet.fileList]

    if toProcessQueue:
        da_res = process_file(
            tpSet.open_data(
                toProcessQueue.pop()
            )
        )
    while toProcessQueue:
        da_res = xr.concat(
            [da_res, process_file(
                tpSet.open_data(
                    toProcessQueue.pop()
                )
            )],
            dim='time'
        )

    return mean_over_time(
        da_res, span=3, edges=False
    )



###############################################################
#
#       Running script
#

wsPath: str = (
    '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/continuous_0.5.pkl'
)
with open(wsPath, 'rb') as inp:
    tpSet: Weatherset = pickle.load(inp)

# Automatically run this script if the file is called as main
if __name__ == "__main__":

    res: xr.DataArray = main()
    res.to_netcdf(
        'data/retrieved-rea.nc'
    )