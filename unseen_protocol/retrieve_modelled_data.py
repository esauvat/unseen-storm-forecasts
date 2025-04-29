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
#
# The resulting DataArray will be of the following format:
#
#   - Dimensions : [ "number", "time", "idate"]
#   - Coordinates :
#       • "number" : ensemble member identification
#               (for hincdast will be in [1,2,3,4,5,6,7,8,9,10,51])
#       • "time" : lead time as int
#       • "idate" :
#           → file date (to differentiate the same hindcasts)
#           → hindcast date
#

import pickle
from sys import argv

import numpy as np
import xarray as xr

from weatherdata.classes import Weatherset
from weatherdata.geographics import apply_curv_weights



tpSet: Weatherset = None
hansLats: slice(float, float) = slice(62.5, 60.5)
hansLongs: slice(float, float) = slice(9., 11.5)
firstUncorrelated: int = 15


###############################################################
#
#   Auxiliary functions
#

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
        #
        #   ### This part is no longer used, we have now decided to keep all
        #   the ensemble members, and not select anything past 26-06-2023 ###
        #
        # # Selecting the proper ensemble numbers
        # if tpSet.multiType:
        #     numberIndexer = xr.DataArray(
        #         np.array(list(range(10)) + [ 50 ]),
        #         dims="number"
        #     )
        #     da = da.isel(
        #         number=numberIndexer
        #     )
        # else:
        #     numberIndexer = xr.DataArray(
        #         np.arange(51),
        #         dims="number"
        #     )
        #     da = da.isel(
        #         number=numberIndexer
        #     )

    res = da.expand_dims(
        {"fdate": [initDate]}
    ).stack(
        idate = ["hdate", "fdate"]
    ).reset_index("idate")

    return res


def process_file(
        key: tuple[ str, str ]
) -> xr.DataArray:
    fileType, fileName = key
    da = xr.open_dataarray(
        tpSet.pathsToFiles[ key ]
    ).sel(
        latitude=hansLats,
        longitude=hansLongs,
    )
    da = apply_curv_weights(da)
    da = da.mean(
        [ "latitude", "longitude" ]
    )
    str_initDate: str = fileName[-10:]
    dt64_initDate: np.datetime64 = np.datetime64(str_initDate)

    da = refactor_coords(da, str_initDate)

    firstUncoDate: np.datetime64 = (
            dt64_initDate + np.timedelta64(firstUncorrelated, 'D'))
    da = da.where(
        da.time >= firstUncoDate,
        drop=True
    )
    newTimes: np.ndarray[tuple[int,], int] = (
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

def main() -> xr.DataArray:
    """
    Select the averaged total precipitation over Hans area and create a single data array.
    """

    da_res: xr.DataArray = None

    toProcessQueue: list[tuple] = []
    for key in tpSet.fileList:
        if key[1][-10:] <= '2023-06-26':
            toProcessQueue.append(key)

    if toProcessQueue:
        da_res = process_file(toProcessQueue.pop())
    while toProcessQueue:
        da_res = xr.concat(
            [ da_res, process_file(toProcessQueue.pop()) ],
            dim="idate"
        )

    da_res.name = "tp24"

    # Save the DataArray
    forecast: bool = True
    hindcast: bool = True
    if len(argv) >= 2:
        forecast = (argv[ 1 ] != "hindcast")
        hindcast = (argv[ 1 ] != "forecast")

    if forecast and hindcast:
        files = "full"
    elif forecast:
        files = "forecast"
    else:
        files = "hindcast"
    da_res.to_netcdf(
        'data/retrieved-' + files + ".nc"
    )

    return da_res


###############################################################
#
#   Run the script
#

if __name__ == "__main__":

    wsPath: str = None
    if len(argv) >= 2 and argv[ 1 ] == "forecast":
        wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_0.5_forecast.pkl'
    elif len(argv) >= 2 and argv[ 1 ] == "hindcast":
        wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_0.5_hindcast.pkl'
    else:
        wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_0.5.pkl'

    with open(wsPath, 'rb') as inp:
        tpSet = pickle.load(inp)

    main()
