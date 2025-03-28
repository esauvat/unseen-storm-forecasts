""" We want to compute the correlation between ensemble members over Hans' area. This file will use 
the norm approach : we store the norm of the correlation matrice. The idea will be to plot the anomaly of 
the norms, ie we substract sqrt(n) which is the minimal norm of the correlation matrice. """

###   Packages 

import pickle

import numpy as np
import xarray as xr

import weatherdata as wd



###   Opening the dataset

wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_0.5.pkl'  # Path to the dataset

with open(wsPath, 'rb') as inp:
    tpSet = pickle.load(inp)

###   Variables

arraysList = []  # Initialize a list to store the arrays of correlation depending on lead time before concatenation

resDir = '/nird/projects/NS9873K/emile/heavy_files/'
# The final array's size will be about 75MB, hence we store them
# outside the git repo

lats = slice(62.5, 60.5)  # Hans area latitudes indexes
longs = slice(9, 11.75)  # Hans area longitudes indexes


###   Function

def process_file(arr: xr.DataArray) -> None:
    global arraysList
    arr = arr.sel(latitude=lats, longitude=longs)  # Selecting hans area
    fileDate = np.datetime64(key[1][-10:]).astype('datetime64[D]').astype(int)
    arr['time'] = np.array(
        [  # Reindex the lead times to have the length of the model
            (day.astype('datetime64[D]').astype(int) - fileDate) for day in arr['time'].values
        ]
    )
    arr = arr.reindex({"time":np.arange(15, 46)})
    arr = wd.pearson_correlation(arr).to_dataset(dim="hdate")  # Compute the correlations statistics (norm, mean, std)
    for var in arr.data_vars:
        arraysList.append(arr[var])
    arr.close()


###   Processing

for key in tpSet.fileList:
    data = tpSet.open_data(key)
    process_file(data)

name = 's2s-hans_area-' + tpSet.resolution + '-correlation_statistics'
path = resDir + name + '.nc'

res = xr.concat(arraysList, dim="model")
res.name = "HA-correlation_statistics"
res.to_netcdf(path)
del arraysList

tpSet.compute[name] = path

with open(wsPath, 'wb') as outp:
    pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)
