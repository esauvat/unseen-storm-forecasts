
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

wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_0.5.pkl'

with open(wsPath, 'rb') as inp:
    tpSet = pickle.load(inp)


###   Variables

dataarrays = []

dir = '/nird/projects/NS9873K/emile/heavy_files/'

lats = slice(62.5, 60.5)
longs = slice(9, 11.75)

argType = sys.argv[1]
dictType = dict(
    daily = None,
    mean2 = 2,
    mean3 = 3
)
type = dictType[argType]


###   Function

def process_file(data:xr.DataArray) -> None :
    global dataarrays
    data = data.sel(latitude=lats, longitude=longs).mean(dim=["latitude","longitude"])                      # Selecting the mean over hans' area
    if type:
        data = wd.mean_over_time(data, type, False)
    data = wd.spearman_rank_correlation(data).to_dataset(dim="hdate")
    for var in data.data_vars:
        arr = data[var]
        arr.name = str(arr.name)
        dataarrays.append(arr)
        arr.close()
    data.close()


###   Processing

for key in tpSet.fileList:
    data = tpSet.open_data(key)
    process_file(data)
    data.close()

name = 's2s-' + tpSet.resolution + '-' + argType + '_correlation-hans_area'
path = dir + name + '.nc'

xr.concat(dataarrays, dim="date").to_netcdf(path)
del dataarrays

tpSet.compute[name] = path

with open(wsPath, 'wb') as outp:
    pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)