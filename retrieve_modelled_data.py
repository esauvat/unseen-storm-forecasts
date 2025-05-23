#
# First step of the UNSEEN protocol, after having explored the data enough so we can
# determine a proper definition of the wanted events.
#
# The target domain will be the center of Norway :
#   - latitude range from 62.5 to 60.5
#   - longitude range from 9 to 11.5
# We use the 0.5° resolution forecast and hindcast
#

#
# In the dataset, some initialization dates are shared (speaking on only the month/day couple).
# This means we can't just reunite the initialization date and hdate coordinate by matching the
# hindcast year to the initialization's one, or we would have some overlap.
#
# It's also unreasonnable to create a file date coordinates. Because of how small the number of
# overlaping dates is, we would end up with a very big array almost half full of NaN values.
#
# This leaves us with two options:
#   - Create a Dataset instead of a DataArray to have different time coordinates
#   - Stack the hdate, time and initialization into a multiIndex coordinate before unidexing,
#   leaving us with an unidexed dimension and uncannonical coordinates to access it.
#
# The first option is much cleaner in terms of coordinates, but is kind of a missuse of the
# Dataset objects, given that the data are the same physical properties, and most of the
# variables don't overlap in time
#
# The second option offers a single DataArray, which is much easier to handle when computing
# statistics, however specific day's data may be less clean to access.
#
# We will use (for now at least) the second option, given that it is the one we already use
# in other scripts. This decision may change in the future.
#
# The resulting DataArray will be of the following format:
#
#   - Dimensions : [ "number", "time", "idate"]
#   - Coordinates : int
#       • "number" : ensemble member identification
#               (for hincdast will be in [1,2,3,4,5,6,7,8,9,10,51])
#       • "time" : lead time as int
#       • "idate" :
#           → file date (to differentiate the same hindcasts)
#           → hindcast date
#

from sys import argv

import numpy as np
import xarray as xr
from numpy.typing import NDArray

from weatherdata import sum_over_time
from weatherdata.geographics import apply_curv_weights



hansLats: slice(float, float) = slice(62.5, 60.5) # type: ignore
hansLongs: slice(float, float) = slice(9., 11.5) # type: ignore
firstUncorrelated: int = 15


###############################################################
#
#   Auxiliary functions
#

def get_list(
        type: str = ''
) -> list[str] :
    """
    Get the list of netCDF files
    """

    dates = np.concat(
        [np.arange(
            np.datetime64('2020-01-02'),
            np.datetime64('2023-06-26'),
            np.timedelta64(7, 'D')
        ), np.arange(
            np.datetime64('2020-01-06'),
            np.datetime64('2023-06-26'),
            np.timedelta64(7, 'D')
        )]
    )

    dates = np.datetime_as_string(dates)

    if type == "forecast":
        files = [
            '/nird/projects/NS9873K/etdu/processed/cf-forsikring/s2s/ecmwf/forecast/daily/values/tp24/tp24_0.5x0.5_'+date+'.nc'
            for date in dates
        ]
    elif type == "hindcast":
        files = [
            '/nird/projects/NS9873K/etdu/processed/cf-forsikring/s2s/ecmwf/forecast/daily/values/tp24/tp24_0.5x0.5_' + date + '.nc'
            for date in dates
        ]
    else :
        files = [
            '/nird/projects/NS9873K/etdu/processed/cf-forsikring/s2s/ecmwf/forecast/daily/values/tp24/tp24_0.5x0.5_' + date + '.nc'
            for date in dates
        ] + [
            '/nird/projects/NS9873K/etdu/processed/cf-forsikring/s2s/ecmwf/hindcast/daily/values/tp24/tp24_0.5x0.5_' + date + '.nc'
            for date in dates
        ]

    return files


def refactor_coords(
        da: xr.DataArray,
        initDate: str
) -> xr.DataArray:
    """
    Change the coordinates system and adjust the number indexes,
    if needed
    """

    if not "hdate" in da.coords:
        hdateIdx: int = (
            int("".join(initDate.split('-')))
        )
        da = da.expand_dims(
            {"hdate": [hdateIdx]},
        )

    res = da.expand_dims(
        {"fdate": [initDate]}
    ).stack(
        idate = ["hdate", "fdate"]
    ).reset_index("idate")

    return res


def process_file(
        path: str
) -> xr.DataArray:
    da = xr.open_dataarray(
        path
    ).sel(
        latitude=hansLats,
        longitude=hansLongs,
    )
    da = apply_curv_weights(da)

    # Remove negative values
    da = xr.where(da>=0, da, 0)

    da = da.mean(
        [ "latitude", "longitude" ]
    )
    str_initDate: str = path[-13:-3]
    dt64_initDate: np.datetime64 = np.datetime64(str_initDate)

    da = refactor_coords(da, str_initDate)

    firstUncoDate: np.datetime64 = (
            dt64_initDate + np.timedelta64(firstUncorrelated, 'D'))
    da = da.where(
        da.time >= firstUncoDate,
        drop=True
    )
    newTimes: NDArray = (
        np.array([
            (time.astype('datetime64[D]')-dt64_initDate).astype(int)
            for time in da.time.values
        ]))
    da = da.assign_coords(
        time=newTimes
    )

    return da


###############################################################
#
#   Main functions
#

def main(
        files: list[str]
) -> xr.DataArray:
    """
    Select the averaged total precipitation over Hans area and create a single data array.
    """

    da_res: xr.DataArray = None # type: ignore

    if files:
        da_res = process_file(files.pop())
    while files:
        da_res = xr.concat(
            [ da_res, process_file(files.pop()) ],
            dim="idate"
        )

    da_res.values = da_res.values * 1000
    da_res.name = "tp24"

    # Save the DataArray
    forecast: bool = True
    hindcast: bool = True
    if len(argv) >= 2:
        forecast = (argv[ 1 ] != "hindcast")
        hindcast = (argv[ 1 ] != "forecast")

    if forecast and hindcast:
        dataName = "full"
    elif forecast:
        dataName = "forecast"
    else:
        dataName = "hindcast"

    sum_over_time(da_res, span=3, edges=False).to_netcdf(
        'data/retrieved-' + dataName + ".nc"
    )

    return da_res


###############################################################
#
#   Run the script
#

if __name__ == "__main__":

    if len(argv) >= 2 and argv[ 1 ] == "forecast":
        filesList = get_list("forecast")
    elif len(argv) >= 2 and argv[ 1 ] == "hindcast":
        filesList = get_list("hindcast")
    else:
        filesList = get_list()

    main(filesList)
