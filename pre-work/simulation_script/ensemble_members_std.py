""" Computing the standard deviation between ensemble members """

###############################################################
#       Packages

import numpy as np
import xarray as xr

import weatherdata as wd
from weatherdata.classes import Weatherset
from weatherdata.functions import combine_4_files_ha



###############################################################
#       Inner variables

# List of DataArray before concatenation
resList = []

# End folder to store the computed data
storingDir = ('/nird/projects/NS9873K/emile/unseen-storm-forecasts'
              '/weathersets/results/')

# Hans' areas boundValues
lats = slice(
    62.75, 60.5)
longs = slice(
    9, 11.75)

# Shared numbers values between hindcasts and forecasts
numbers = np.array(
    list(
        range(
            1, 11)) + [51])

# Dictionary to convert treatment type into time span
typeDict = {
    "daily":None, "mean2":2, "mean3":3 }


###############################################################
#       Auxiliary functions

def process_init_date(
        tpSet: Weatherset,
        fileDate: str,
        treatmentType: str | None = "daily"
) -> None:
    global resList

    data = combine_4_files_ha(
        fileDate, tpSet).sel(
        number=numbers)
    data.coords['time'] = np.array(
        [wd.date_as_int(
            day) - wd.date_as_int(
            fileDate) for day in data.coords['time'].values])

    span = typeDict[treatmentType]
    if span:
        data = wd.mean_over_time(
            data, span=span, edges=False)

    def members_std(
            arr
    ):
        return np.std(
            arr, axis=2)

    data = xr.apply_ufunc(
        members_std, data,
        input_core_dims=[["number"]],
        output_core_dims=[[]])
    data = data.expand_dims(
        { "fdate":[fileDate] }).stack(
        sim=["fdate", "hdate"]).reset_index(
        "sim")
    resList.append(
        data)
    del data

    ### END ###


###############################################################
#       Main function

def compute_std(
        tpSet: Weatherset,
        lastDate: str,
        treatmentType: str | None = "daily"
) -> None:
    global resList

    resList = []  # Reseting the resList

    ##########################################
    # Get all the initialization dates

    # Get the dates as string, each date correspond to at most 2 hindcast
    # and 2 forecast files
    initDates = np.unique(
        [fileName[-10:] for _, fileName in tpSet.fileList])
    # Reduce the working dataset to dates with exactly 4 associated files
    initDates = initDates[initDates <= lastDate]
    ##########################################

    for date in initDates:
        process_init_date(
            tpSet, date, treatmentType)

    result = xr.concat(
        resList, dim='sim')
    resList = []
    name = "s2s-HA_avg-all_res-ensemble_std-" + treatmentType
    path = storingDir + name + ".nc"
    result.to_netcdf(
        path)

    tpSet.compute[name] = path

    ### END ###


###############################################################
#
#       Run the program
#

if __name__ == "__main__":

    wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_all-res.pkl'

    import pickle



    with open(
            wsPath, 'rb') as inp:
        set = pickle.load(
            inp)

    compute_std(
        set, '2021-01-01', "mean2")
    compute_std(
        set, '2021-01-01', "mean3")

    with open(
            wsPath, 'wb') as outp:
        pickle.dump(
            set, outp, pickle.HIGHEST_PROTOCOL)