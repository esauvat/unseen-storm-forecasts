""" This file regroup all the correlation related script """

###############################################################
#       Packages


from itertools import product
from typing import Any

import numpy as np
import xarray as xr

import weatherdata as wd
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
        treatmentType: str | None = "daily"
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

        res = xr.concat(
            [
                data1.sel(
                    latitude=lats,
                    longitude=longs).mean(
                    dim=["latitude", "longitude"]),
                data2.sel(
                    latitude=lats,
                    longitude=longs).mean(
                    dim=["latitude", "longitude"])],
            dim="time")
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
            edges=False,
            center=False).isel(time=slice(0,-span+1))

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
        a = tpSet.open_data(
            keys[0]).sel(
            latitude=lats,
            longitude=longs
        ).mean(
            ["latitude", "longitude"])
        b = tpSet.open_data(
            keys[1]).sel(
            latitude=lats,
            longitude=longs
        ).mean(
            ["latitude", "longitude"])
        forecast = xr.concat(
            [a, b],
            dim="time"
        ).sel(
            number=numbers)
        a = tpSet.open_data(
            keys[2]).sel(
            latitude=lats,
            longitude=longs
        ).mean(
            ["latitude", "longitude"])
        b = tpSet.open_data(
            keys[3]).sel(
            latitude=lats,
            longitude=longs
        ).mean(
            ["latitude", "longitude"])
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
        forecast = tpSet.open_data(
            tuple(
                keys[0])).sel(
            latitude=lats,
            longitude=longs,
            number=numbers
        ).mean(
            ["latitude", "longitude"])
        hindcast = tpSet.open_data(
            tuple(
                keys[1])).sel(
            latitude=lats,
            longitude=longs,
        ).mean(
            ["latitude", "longitude"])

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
            edges=False,
            center=False
        )

    return data.sel(
        time=targetDay
    )

    ### END ###


###############################################################
#       Main functions

def hans_area_avg_correlation(
        tpSet: Weatherset,
        treatmentType: str | None = "daily",
        lastDate: str | None = '2022-12-29'
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
            treatmentType)
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

    ### END ###


def hans_area_avg_correlation_stepped(
        tpSet: Weatherset,
        treatmentType: str | None = "daily",
        lastDate: str | None = '2022-12-29'
) -> None:
    """ Compute the correlation between ensemble members per lead time"""
    ### Initialize variables
    global arraysList  # Access global variable
    arraysList = []  # Initialize by setting to empty list
    assert tpSet.resolution is None, ("This function need files of both "
                                      "resolutions")
    str_resolution = 'all_res'
    timeSpan = typeDict[treatmentType]

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
    # Process one lead time at a time
    results = []
    for ltime in np.arange(45):

        ##########################################
        # Compute the wanted data for each initDate
        for date in initDates:
            data = open_arrays(
                date,
                ltime,
                tpSet,
                timeSpan,
            )
            targetDay = np.datetime64(date) + np.timedelta64(ltime, 'D')
            data = process_files_one_ltime(
                data,
                targetDay,
                timeSpan
            )
            arraysList.append(
                data.expand_dims(
                    {"fdate":np.array([date])}
                )
            )
            del data
        ##########################################

        results.append(
            xr.concat(
                arraysList,
                dim="fdate"
            ).expand_dims(
                {"ltime":np.array([ltime])}
            ).stack(
                obs=["fdate", "hdate"]
            ).reset_index("obs")
        )
        arraysList = []
    ##########################################

    ##########################################
    # Compute the correlation (distribution and between numbers)
    resArray = xr.concat(
        results,
        dim="ltime"
    )
    del results
    resArray = xr.apply_ufunc(
        wd.pears_distrib,
        resArray,
        input_core_dims=[["number","obs"]],
        output_core_dims=[["correlations"]],
        vectorize=True
    )

    name = (
            's2s-HA_avg-' + str_resolution + '-correlation_1_on_1-' +
            treatmentType)
    path = storingDir + name + '.nc'

    resArray.to_netcdf(
        path)
    tpSet.compute[name] = path
    ##########################################

    ### END ###


# ###############################################################
# #       Tests

# import pickle

# with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts
# /weathersets/s2s_all-res.pkl', 'rb') as inp:
#     tpSet = pickle.load(inp)

# test_keys = [
#     ('forecast','tp24_0.25x0.25_2022-12-29'),
#     ('forecast','tp24_0.5x0.5_2022-12-29'),
#     ('hindcast','tp24_0.25x0.25_2022-12-29'),
#     ('hindcast','tp24_0.5x0.5_2022-12-29')
# ]

# process_4_files(
#     test_keys,
#     '2022-12-29',
#     tpSet,
#     "mean2"
# )
