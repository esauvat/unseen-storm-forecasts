
""" This file regroup all the correlation related script """

###############################################################
#       Packages


import weatherdata as wd
from weatherdata.classes import composite_dataset as Weatherset
import numpy as np
import xarray as xr
from itertools import product
from typing import Any



###############################################################
#       Inner variables

    # List of DataArray before concatenation
arraysList: list[Any] = []

    # End folder to store the computed data
storingDir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/'

    # Hans' areas boundaries
lats = slice(62.75, 60.5)
longs = slice(9, 11.75)

    # Dictionary to convert treatment type into time span
typeDict = {
    "daily" : None,
    "mean2" : 2,
    "mean3" : 3
}



###############################################################
#       Auxiliary functions

def process_4_files(
    keys : list[tuple[str,str]],
    fileDate : str,
    tpSet : Weatherset,
    treatmentType : str | None = "daily"
) -> None :
    
    global arraysList
    
        # Utility function to concatenate the 2 different resolutions of a simulation
    def concat_over_time(
        data1 : xr.DataArray,
        data2 : xr.DataArray
    ) -> xr.DataArray :
        """ The 2 data arrays must be of the same type : either both forecast or both hindcast """
        
        assert ('hdate' in data1.dims) == ('hdate' in data2.dims), "can't concatenate \
        a forecast and a hindcast over the time dimension"
        
        res = xr.concat(
            [
                data1.sel(latitude=lats, longitude=longs).mean(dim=["latitude","longitude"]),
                data2.sel(latitude=lats, longitude=longs).mean(dim=["latitude","longitude"])
            ],
            dim="time"
        )
        return res
    
        # Create the forecast array
    hRes = xr.open_dataarray(tpSet.pathsToFiles[keys[0]])
    lRes = xr.open_dataarray(tpSet.pathsToFiles[keys[1]])
    forecast = concat_over_time(
        hRes, lRes
    ).expand_dims(                         # Add a hdate dimension to prepare the concatenation with the hindcast array
        {"hdate":[int("".join(fileDate.split('-')))]}       # The coordinate is the file date on the hdate format (int)
    )
    
        # Create the hindcast array
    hRes = xr.open_dataarray(tpSet.pathsToFiles[keys[2]])
    lRes = xr.open_dataarray(tpSet.pathsToFiles[keys[3]])
    hindcast = concat_over_time(
        hRes, lRes
    )                                                       # No need to add a hdate dimension since it already exists
    
    del hRes        # Delete to free some memory
    del lRes        # Delete to free some memory
    
        # Create the final data :
    data = xr.concat(
        [hindcast, forecast],
        dim="hdate"
    )
    
    del forecast    # Delete to free some memory
    del hindcast    # Delete to free some memory
    
        # If needed, compute the averaged precipitations
    span = typeDict[treatmentType]
    if span :
        data = wd.mean_over_time(
            data, span, edges = False
        )
    
        # Change the time coordinates to the lead time as int
    intFileDate = wd.date_as_int(np.datetime64(fileDate))
    data.coords['time'] = np.array([
        (wd.date_as_int(datetime) - intFileDate) for datetime in data.coords['time'].values
    ])
    
    arraysList.append(
        data.expand_dims({"fdate":[fileDate]})
    )

    del data
    
    ### END ###



# def process_files_one_res(
#     fileDate : str,
#     timeSlice : slice,
#     tpSet : Weatherset,
# ):



###############################################################
#       Main functions

def hans_area_avg_correlation(
    tpSet : Weatherset,
    treatmentType : str | None = "daily",
    lastDate : str | None = '2022-12-29'
) -> None :

    """ Compute the correlation between ensemble members per lead time
    over the dataset, each model and hindcast date is considered as an
    observation of each of the ensemble variables."""
    
        ### Initialize variables
    global arraysList                       # Access global variable
    arraysList = []                         # Initialize by setting to empty list
    assert tpSet.resolution is None, "This function need files of both resolutions"
    resolution = 'all_res'
    
        ##########################################
        # Get all the initialization dates

    # Get the dates as string, each date correspond to at most 2 hindcast and 2 forecast files
    initDates = np.unique([fileName[-10:] for _,fileName in tpSet.fileList])
    # Reduce the working dataset to dates with exactly 4 associated files
    initDates = initDates[initDates <= lastDate]
        ##########################################
    
        ##########################################
        # Run process 4 files to all the dates
    fileTypes = ['forecast', 'hindcast']                # 2 possible file type
    
    for date in initDates :
        
        fileNames = [                                   # 2 possible resolution
            'tp24_0.25x0.25_' + date,
            'tp24_0.5x0.5_' + date
        ]
        
        keys = list(product(                            # Apply set product -> 4 names associated to the date
            fileTypes, fileNames
        ))
        
        process_4_files(                                # Run function
            keys, date, tpSet, treatmentType
        )
        ###########################################
    
    data = xr.concat(              
        arraysList, dim="fdate"
    ).stack(        # Stacking file date and hindcast date as observations
        obs = ["fdate","hdate"]
    )
    arraysList = []     # Reseting arraysList
    
        ###########################################
        # Compute the correlation (distribution and between numbers)
        
        # Correlation 1 to 1
    corr_distrib = xr.apply_ufunc(       
        # Use apply ufunc to run np.corrcoef for each time
        wd.pears_distrib, data,
        input_core_dims=[["number","obs"]],
        output_core_dims=[["correlations"]],
        vectorize=True                                  # Vectorize to pass 2-D arrays to np.corrcoef
    )
    
    name = 's2s-HA_avg-'+resolution+'-correlation_1_on_1-'+treatmentType
    path = storingDir + name + '.nc'
    
    corr_distrib.to_netcdf(path)
    tpSet.compute[name] = path
    
    del corr_distrib
    
        # Ensemble correlation
    ensemble_corr = xr.apply_ufunc(
        wd.pears, data,
        input_core_dims=[["number"]],
        output_core_dims=[[]],
        vectorize=True
    )
    
    name = 's2s-HA_avg-'+resolution+'-ensemble_correlation-'+treatmentType
    path = storingDir + name + '.nc'
    
    ensemble_corr.to_netcdf(path)
    tpSet.compute[name] = path
    
    del ensemble_corr
    ###############################################
    
    del data
    
    ### END ###



# ###############################################################
# #       Tests

# import pickle

# with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_all-res.pkl', 'rb') as inp:
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


