#
# Run some preprocessing over the data, ie:
#   - accumulating over 3 consecutive days
#   - selecting the max for each month and determine the overlap month
#

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"

from sys import argv

import xarray as xr
import numpy as np
import datetime
from weatherdata import date_as_int



###############################################################
#
#       Functions
#


def determine_overlap_month(
        initDate: np.datetime64,
) -> int:
    """
    Determine which month overlap the most with the initialization date
    given and return its number
    """
    
    # Define the time extent
    firstDate = initDate + np.timedelta64(15,'D')
    lastDate = initDate + np.timedelta64(43, 'D')

    # First check if a full month exists between the dates
    firstMonth: int = firstDate.astype('datetime64[M]').astype(int)
    lastMonth: int = lastDate.astype('datetime64[M]').astype(int)
    if (lastMonth - firstMonth) == 2:
        return ((firstMonth + 1) % 12) + 1
    else:
        # Determine the lenght of the extent:
        lenght: int = (lastDate - firstDate).astype(int)
        lastDay = (lastDate - lastDate.astype('datetime64[M]')).astype(int) + 1
        if lastDay >= (lenght // 2):
            return lastMonth % 12 + 1
        else:
            return firstMonth % 12 + 1


def maximize(
        da: xr.DataArray,
) -> xr.DataArray:
    """
    Select the maximum of each simulation
    """

    firstOffset, lastOffset = (
        da.time.values[0], da.time.values[-1]
    )
    
    olMonths = np.array([
        determine_overlap_month(d)
        for d in da.date.values
    ])
    
    return da.assign_coords(
        month = ("date", olMonths)
    )


###############################################################
#
#       Running
#

if __name__ == '__main__':

    if len(argv) >= 2 and argv[1] == "hindcast":
        data = xr.open_dataarray('data/retrieved-hindcast.nc')
        files="hindcast"
    elif len(argv) >= 2 and argv[1] == "forecast":
        data = xr.open_dataarray('data/retrieved-forecast.nc')
        files="forecast"
    else:
        data = xr.open_dataarray('data/retrieved-full.nc')
        files="full"

    res = maximize(
        data
    )

    res.to_netcdf('data/processed-'+files+'.nc')
    
    res.max(dim="time").to_netcdf('data/maxs-'+files+'.nc')