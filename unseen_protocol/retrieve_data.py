#
# First step of the UNSEEN protocol, after having explore the data enough so we can
# determine a proper definition of the wanted events.
#
# The target domain will be the center of Norway :
#   - latitude range from 62.5 to 60.5
#   - longitude range from 9 to 11.5
# We use the 0.5° resolution forecast and hindcast
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


###############################################################
#
#   Auxiliary functions
#

def reindex_hindcast(
        ds: xr.Dataset,
) -> xr.DataArray:
    """
    For hindcast files, change the time so it shows the real time
    """

    #
    # In the dataset, some initialization dates are shared (speaking on only the month/day couple).
    # This means we can't just stack the initialization date and hdate coordinate and to
    # match the hindcast initialization, or we would have some overlap.
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
    #   - Dimensions : [ "number", "time"]
    #   - Coordinates :
    #       • "number" : ensemble member identification
    #               (for hincdast will be in [1,2,3,4,5,6,7,8,9,10,51])
    #       • "time" : multiIndex representing the time specifics:
    #           → real time of the simulation
    #               (time as in the original file with corrected hindcast year)
    #           → file date
    #               (this coordinate is used to differentiate the overlaping dates)
    #

    str_arrDate: str = ds.initDate
    arr: xr.DataArray = ds.tp24.rename(str_arrDate)
    del ds

    dt64_arrDate: np.datetime64 = np.datetime64(str_arrDate)

    def hdate_to_dt64(
            hd: str
    ) -> np.datetime64:
        str_hd: str = "-".join([
            hd[ :4 ], hd[ 4:6 ], hd[ 6: ]
        ])
        return np.datetime64(str_hd)

    list_newTimesIndexes: list[ np.datetime64 ] = [ ]
    for hind in arr.hdate.values:
        dt64_hind: np.datetime64 = hdate_to_dt64(str(hind))
        for date in arr.time.values:
            timeOffset: np.timedelta64 = date.astype('datetime64[D]') - dt64_arrDate
            nDate: np.datetime64 = dt64_hind + timeOffset
            list_newTimesIndexes.append(nDate)
    newTimesIndexes = np.array(
        list_newTimesIndexes
    )
    del list_newTimesIndexes

    arr = arr.stack(htime=[ "hdate", "time" ]).reset_index("htime")
    arr = arr.reindex(
        { "htime":newTimesIndexes }
    ).drop_vars([ "hdate", "time" ])

    res: xr.DataArray = arr.expand_dims(
        { "fdate":[ str_arrDate ] }
    ).stack(
        time=[ "htime", "fdate" ]
    ).reset_index("time")

    return res


def reindex_forecast(
        ds: xr.Dataset
) -> xr.DataArray:
    """
    For forecast files, when the total set includes both hindcasts and forecasts files,
    this function is simply used to set forecast files in the same format as hindcast ones
    """

    str_arrDate: str = ds.initDate

    if tpSet.multiType:
        numberIndexer = xr.DataArray(
            np.array(list(range(10)) + [ 50 ]),
            dims="number"
        )
        arr: xr.DataArray = ds.tp24.isel(
            number=numberIndexer
        ).rename(str_arrDate)

        res: xr.DataArray = arr.rename(
            { "time":"htime" }
        ).expand_dims(
            { "fdate":[ str_arrDate ] }
        ).stack(
            time=[ "htime", "fdate" ]
        ).reset_index("time")
    else:
        numberIndexer = xr.DataArray(
            np.arange(51),
            dims="number"
        )
        res: xr.DataArray = ds.tp24.isel(
            number=numberIndexer
        ).rename(str_arrDate)

    return res


###############################################################
#
#   Main functions
#

def main() -> xr.DataArray:
    """
    Select the averaged total precipitation over Hans area and create a single data array.
    """

    da_res: xr.DataArray = None

    def process_file(
            key: tuple[ str, str ]
    ) -> xr.DataArray:
        fileType, fileName = key
        ds = xr.open_dataset(
            tpSet.pathsToFiles[ key ]
        ).sel(
            latitude=hansLats,
            longitude=hansLongs
        )
        ds = apply_curv_weights(ds)
        ds[ 'tp24' ] = ds[ 'tp24' ].mean(
            [ "latitude", "longitude" ]
        )
        ds.attrs["initDate"] = fileName[-10:]
        if fileType == "hindcast":
            da = reindex_hindcast(ds)
        else:
            da = reindex_forecast(ds)

        return da

    if tpSet.fileList:
        da_res = process_file(tpSet.fileList[ 0 ])
    if len(tpSet.fileList) > 1:
        for elem in tpSet.fileList[ 1: ]:
            da_res = xr.concat(
                [ da_res, process_file(elem) ],
                dim="time"
            )

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

wsPath: str = None
if len(argv) >= 2 and argv[ 1 ] == "forecast":
    wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_0.5_forecast.pkl'
elif len(argv) >= 2 and argv[ 1 ] == "hindcast":
    wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_0.5_hindcast.pkl'
else:
    wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_0.5.pkl'

with open(wsPath, 'rb') as inp:
    tpSet = pickle.load(inp)

if __name__ == "__main__":
    main()
