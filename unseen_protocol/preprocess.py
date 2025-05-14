#
# Run some preprocessing over the data, ie:
#   - accumulating over 3 consecutive days
#   - selecting the max for each month and determine the overlap month
#

from sys import argv

import xarray as xr
import numpy as np
from weatherdata import date_as_int, sum_over_time



###############################################################
#
#       Functions
#


def determine_overlap_month(
        firstDate: np.datetime64,
        lastDate: np.datetime64
) -> int:
    """
    Determine which month overlap the most with the time extent given by firstDate
    and lastDate and return its number
    """

    # First check if a full month exists between the dates
    firstMonth: int = firstDate.astype(object).month
    lastMonth: int = lastDate.astype(object).month
    firstMonthNumber: int = firstDate.astype('datetime64[M]').astype(int)
    lastMonthNumber: int = lastDate.astype('datetime64[M]').astype(int)
    if (lastMonthNumber - firstMonthNumber) == 2:
        return (firstMonth + 1) % 12
    else:
        # Determine the lenght of the extent:
        lenght: int = date_as_int(lastDate) - date_as_int(firstDate)
        lastDayNumber = lastDate.astype(object).day
        if lastDayNumber >= (lenght // 2):
            return lastMonth
        else:
            return firstMonth


def maximize(
        da: xr.DataArray,
) -> xr.Dataset:
    """
    Select the maximum of each simulation
    """

    firstOffset, lastOffset = (
        da.time.values[0], da.time.values[-1]
    )

    valMaxs = da.max(dim="time")
    dateMaxs = da.idxmax(dim="time")
    olMonths = xr.concat(
        [
            xr.full_like(
                valMaxs.where(valMaxs.fdate==date, drop=True),
                determine_overlap_month(
                    np.datetime64(date)+np.timedelta64(firstOffset, 'D'),
                    np.datetime64(date)+np.timedelta64(lastOffset, 'D')
                )
            )
            for date in np.unique(valMaxs.fdate.values)
        ],
        dim="idate"
    )
    olMonths.values = olMonths.values.astype(int)

    return xr.Dataset(
        data_vars=dict(
            tp24=valMaxs,
            date=dateMaxs,
            month=olMonths
        ),
        coords=valMaxs.coords
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
        sum_over_time(
            data, span=3, edges=False
        )
    )

    res.to_netcdf('data/processed-'+files+'.nc')