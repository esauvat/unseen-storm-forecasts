#
# Retrieve the reanalysis data and store it into a single DataArray to grand quicker access.
#
# This reanalysis data will be used to assess the fidelity of the s2s model.
#

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"

import xarray as xr
import numpy as np

from typing import cast, List

from weatherdata.classes import Weatherset
import weatherdata
from weatherdata.geographics import apply_curv_weights
from weatherdata import sum_over_time


###############################################################
#
#       Functions
#

def process_file(
        path: str,
) -> xr.DataArray:
    """
    Select the wanted data in the reanalysis files, not applying the mean
    """

    da = xr.open_dataarray(path).sel(
        latitude=slice(62.5, 60.5),
        longitude=slice(9, 11.75)
    )
    da = cast(
        xr.DataArray, apply_curv_weights(da)
    ).mean(
        dim=["latitude", "longitude"]
    )
    da.values *= 1000
    return da


def main(
        paths: List,
) -> xr.DataArray:
    """
    Compute a DataArray with all the data and apply the mean over time.

    Arguments:
        paths (List) : list of paths to the different netCDF files.
    """

    da_res: xr.DataArray = None  # type: ignore

    toProcessQueue: List[str] = [p for p in paths]

    if toProcessQueue:
        da_res = process_file(
            toProcessQueue.pop()
        )
    while toProcessQueue:
        da_res = xr.concat(
            [da_res, process_file(
                toProcessQueue.pop()
            )],
            dim='time'
        )

    return da_res


###############################################################
#
#       Running script
#

years = np.arange(
    1941,2025
)
fileList = [
    '/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/continuous-format/daily/tp24/tp24_0.5x0.5_'
    + str(year) + '.nc'
    for year in years
]

# Automatically run this script if the file is called as main
if __name__ == "__main__":
    res = main(fileList)
    res.to_netcdf(
        'data/rea_raw.nc'
    )
