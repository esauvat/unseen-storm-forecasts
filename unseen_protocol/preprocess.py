#
# Run some preprocessing over the data, ie:
#   - averaging over 3 consecutive days
#   - selecting the max for each month and determine the overlap month
#

from sys import argv

import xarray as xr
import numpy as np
from weatherdata import date_as_int, mean_over_time



###############################################################
#
#       Functions
#

# def rolling_by_htime_group(group, winSpan: int = 3):
#     #
#     # The function was written by chatGPT
#     #
#
#     # Get sorted indices by htime (just in case)
#     sorter = np.argsort(group['htime'].values)
#
#     # Sort group by htime
#     group_sorted = group.isel(time=sorter)
#     htime_sorted = group_sorted['htime']
#
#     # We'll apply rolling manually along the 'time' axis
#     values = group_sorted.values
#     rolled = np.full_like(values, np.nan)
#
#     # Looping over each time index to compute rolling mean
#     for i in range(0, len(htime_sorted)-winSpan):
#         # Get window of size winSpan expanding on the right
#         window = values[..., i:i+winSpan]
#         if window.shape[-1] == winSpan:
#             rolled[..., i] = np.nanmean(window, axis=-1)
#
#     # Put the rolled data back into a DataArray
#     result = group_sorted.copy(data=rolled)
#     return result
#
# def rolling_mean_over_htime(
#         da: xr.DataArray,
# ) -> xr.DataArray:
#     da = xr.concat([rolling_by_htime_group(grp) for _, grp in da.groupby('fdate')], dim='time')
#     return da.sortby('time')


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
        mean_over_time(
            data, span=3, edges=False
        )
    )

    res.to_netcdf('data/processed-'+files+'.nc')