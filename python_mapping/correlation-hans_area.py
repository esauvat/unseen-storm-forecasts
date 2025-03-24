
''' We want to compute the correlation between ensemble members in the mean over Hans' area. Since for a specific lead
time, the ensemble member carry only one value, we can rather simply compute the total correlatio between all of the ensemble 
members. This will be much harder when handling all the grid. We will probably start by computing the correlation matrix. '''


###   Packages 

import sys
sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/python_mapping')                       # Path to the python modules
sys.path.append('/home/esauvat/Documents/NORCE/unseen-storm-forecasts/python_mapping')                      # Path to the same directory on the computer to run tests

import weatherdata as wd
import numpy as np, xarray as xr
import pickle


###   Opening the dataset

wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecatst/weathersets/s2s-0.5.pkl'
with open(wsPath, 'rb') as inp:
    tpSet = pickle.load(inp)


###   Variables

dataarrays = []

dir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/'

lats = slice(62.5, 60.5)
longs = slice(9, 11.75)


###   Function

def process_file(data:xr.DataArray) -> None :
    global dataarrays
    data = data.sel(latitude=lats, longitude=longs).mean(dim=["latitude","longitude"])                      # Selecting the mean over hans' area
    data = wd.spearman_rank_correlation(data).to_dataset(dim="hdate")
    for var in data.data_vars:
        dataarrays.append(data[var])
    data.close()


###   Processing

for path in tpSet.pathsToFiles.values():
    process_file(xr.open_dataarray(path))

name = 's2s-' + tpSet.resolution + '-correlation-hans_area'
path = dir + name + '.nc'

xr.concat(dataarrays, dim="date").to_netcdf(path)
del dataarrays

tpSet.compute[name] = path

with open(wsPath, 'wb') as outp:
    pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)