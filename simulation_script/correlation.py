""" This file regroup all the correlation related script """

###############################################################
#       Packages


from itertools import product
from typing import Any

import numpy as np
import xarray as xr

import weatherdata as wd
from weatherdata.geographics import apply_curv_weights
from weatherdata.classes import Weatherset



###############################################################
#       Inner variables

# List of DataArray before concatenation
arraysList: list[Any] = []

# End folder to store the computed data
storingDir = ('/nird/projects/NS9873K/emile/unseen-storm-forecasts'
              '/weathersets/results/')

# Hans' areas boundValues
lats = slice(
    62.75,
    60.5)
longs = slice(
    9,
    11.75)

# Shared numbers values between hindcasts and forecasts
numbers = np.array(list(range(1, 11)) + [51])

# Dictionary to convert treatment type into time span
typeDict = {
    "daily":None, "mean2":2, "mean3":3
}


###############################################################
#       Auxiliary functions

def process_4_files(
        keys: list[list[str]],
        fileDate: str,
        tpSet: Weatherset,
        treatmentType: str | None = "daily",
        avgHA: bool = True
) -> None:
    global arraysList

    # Utility function to concatenate the 2 different resolutions of a
    # simulation
    def concat_over_time(
            data1: xr.DataArray,
            data2: xr.DataArray
    ) -> xr.DataArray:
        """ The 2 data arrays must be of the same type : either both
        forecast or both hindcast """

        assert ('hdate' in data1.dims) == ('hdate' in data2.dims), \
            "can't concatenate \
        a forecast and a hindcast over the time dimension"

        if avgHA:
            data1 = data1.sel(
                latitude=lats,
                longitude=longs
            )
            data1 = apply_curv_weights(data1).mean(
                dim=["latitude", "longitude"]
            )
            data2 = data2.sel(
                latitude=lats,
                longitude=longs
            )
            data2 = apply_curv_weights(data2).mean(
                dim=["latitude", "longitude"]
            )

        res = xr.concat(
            [data1, data2],
            dim="time"
        )
        return res

        # Create the forecast array

    hRes = xr.open_dataarray(
        tpSet.pathsToFiles[tuple(
            keys[0])])
    lRes = xr.open_dataarray(
        tpSet.pathsToFiles[tuple(
            keys[1])])
    forecast = concat_over_time(
        hRes,
        lRes).expand_dims(
        # Add a hdate dimension to prepare the concatenation with the
        # hindcast array
        {
            "hdate":[
                int(
                    "".join(
                        fileDate.split(
                            '-')))] }
        # The coordinate is the file date on the hdate format (int)
    ).sel(
        number=numbers
    )

    # Create the hindcast array
    hRes = xr.open_dataarray(
        tpSet.pathsToFiles[tuple(
            keys[2])])
    lRes = xr.open_dataarray(
        tpSet.pathsToFiles[tuple(
            keys[3])])
    hindcast = concat_over_time(
        hRes,
        lRes)  # No need to add a hdate dimension since it already exists

    del hRes  # Delete to free some memory
    del lRes  # Delete to free some memory

    # Create the final data :
    data = xr.concat(
        [hindcast, forecast],
        dim="hdate")

    del forecast  # Delete to free some memory
    del hindcast  # Delete to free some memory

    # If needed, compute the averaged precipitations
    span = typeDict[treatmentType]
    if span:
        data = wd.mean_over_time(
            data,
            span,
            edges=False)

        # Change the time coordinates to the lead time as int
    intFileDate = wd.date_as_int(
        np.datetime64(
            fileDate))
    data.coords['time'] = np.array(
        [(wd.date_as_int(
            datetime) - intFileDate) for datetime in
         data.coords['time'].values])

    arraysList.append(
        data.expand_dims(
            { "fdate":[fileDate] }))

    del data

    ### END ###


def open_arrays(
        fileDate: str,
        leadTime: int,
        tpSet: Weatherset,
        timeSpan: int | None = None
) -> xr.DataArray:
    def open_array(
            key: tuple[str,str]
    ) -> xr.DataArray:
        arr = tpSet.open_data(
            key
        ).sel(
            latitude=lats, longitude=longs
        )
        return apply_curv_weights(arr).mean(
            dim=["latitude", "longitude"]
        )

    if timeSpan and 15 < leadTime <= 15 + timeSpan:
        fileTypes = [
            'forecast',
            'hindcast',
        ]
        fileNames = [
            'tp24_0.25x0.25_' + fileDate,
            'tp24_0.5x0.5_' + fileDate,
        ]
        keys = list(
            product(
                fileTypes,
                fileNames))
        a = open_array(keys[0])
        b = open_array(keys[1])
        forecast = xr.concat(
            [a, b],
            dim="time"
        ).sel(
            number=numbers)
        a = open_array(keys[2])
        b = open_array(keys[3])
        hindcast = xr.concat(
            [a, b],
            dim="time"
        )
        del a, b
    else:
        if leadTime <= 15:
            dateResolution = '0.25x0.25'
        else:
            dateResolution = '0.5x0.5'
        keys = [
            ['forecast', 'tp24_' + dateResolution + '_' + fileDate],
            ['hindcast', 'tp24_' + dateResolution + '_' + fileDate],
        ]
        forecast = open_array(keys[0]).sel(
            number=numbers
        )
        hindcast = open_array(keys[1])

    return xr.concat(
        [forecast, hindcast],
        dim="hdate")

    ### END ###


def process_files_one_ltime(
        data: xr.DataArray,
        targetDay: np.datetime64,
        timeSpan: int | None = None
) -> xr.DataArray:
    if timeSpan:
        data = data.sel(
            time=slice(
                targetDay - np.timedelta64(
                    timeSpan,
                    'D'),
                targetDay))
        data = wd.mean_over_time(
            data,
            timeSpan,
            edges=False
        )

    return data.sel(
        time=targetDay
    )

    ### END ###


###############################################################
#
#       Main functions
#

def main(
        tpSet: Weatherset,
        treatmentType: str | None = "daily",
        lastDate: str | None = '2022-12-29',
        avgHA: bool = True
) -> None:
    """ Compute the correlation between ensemble members per lead time
    over the dataset, each model and hindcast date is considered as an
    observation of each of the ensemble variables."""

    ### Initialize variables
    global arraysList  # Access global variable
    arraysList = []  # Initialize by setting to empty list
    assert tpSet.resolution is None, ("This function need files of both "
                                      "resolutions")
    resolution = 'all_res'

    ##########################################
    # Get all the initialization dates

    # Get the dates as string, each date correspond to at most 2 hindcast
    # and 2 forecast files
    initDates = np.unique(
        [fileName[-10:] for _, fileName in tpSet.fileList])
    # Reduce the working dataset to dates with exactly 4 associated files
    initDates = initDates[initDates <= lastDate]
    ##########################################

    ##########################################
    # Run process 4 files to all the dates
    fileTypes = ['forecast', 'hindcast']  # 2 possible file type

    for date in initDates:
        fileNames = [  # 2 possible resolution
            'tp24_0.25x0.25_' + date, 'tp24_0.5x0.5_' + date]

        keys = list(
            product(  # Apply set product -> 4 names associated to the date
                fileTypes,
                fileNames))

        process_4_files(  # Run function
            keys,
            date,
            tpSet,
            treatmentType,
            avgHA)
    ###########################################

    data = xr.concat(
        arraysList,
        dim="fdate").stack(
        # Stacking file date and hindcast date as observations
        obs=["fdate", "hdate"])
    arraysList = []  # Reseting arraysList
    data = data.reset_index(
        'obs')

    ###########################################
    # Compute the correlation (distribution and between numbers)

    # Correlation 1 to 1
    corr_distrib = xr.apply_ufunc(
        # Use apply ufunc to run np.corrcoef for each time
        wd.pears_distrib,
        data,
        input_core_dims=[["number", "obs"]],
        output_core_dims=[["correlations"]],
        vectorize=True  # Vectorize to pass 2-D arrays to np.corrcoef
    )

    name = (
            's2s-HA_avg-' + resolution + '-correlation_1_on_1-' +
            treatmentType)
    path = storingDir + name + '.nc'

    corr_distrib.to_netcdf(
        path)
    tpSet.compute[name] = path

    del corr_distrib

    ###############################################

    del data
    pass

    ### END ###


###############################################################
#
#   Run the program
#

if __name__ == '__main__':
    wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_all-res.pkl'

    import pickle



    with open(wsPath, 'rb') as inp:
        set: Weatherset = pickle.load(inp)

    main(set, "mean2", '2021-01-01')
    main(set, "mean3", '2021-01-01')

    with open(wsPath, 'wb') as outp:
        pickle.dump(set, outp, pickle.HIGHEST_PROTOCOL)