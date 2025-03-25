
''' We want to compute the correlation between ensemble members over Hans' area. This file will use 
the norm approach : we store the norm of the correlation matrice. The idea will be to plot the anomaly of 
the norms, ie we substract sqrt(n) which is the minimal norm of the correlation matrice. '''


###   Packages 

import sys
sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/python_mapping')                       # Path to the python modules
sys.path.append('/home/esauvat/Documents/NORCE/unseen-storm-forecasts/python_mapping')                      # Path to the same directory on the computer to run tests

import weatherdata as wd
import numpy as np, xarray as xr
import pickle


###   Opening the dataset

wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_0.5.pkl'                      # Path to the dataset

with open(wsPath, 'rb') as inp:
    tpSet = pickle.load(inp)


###   Variables

dataarrays = []                                                                                             # Initialize a list to store the arrays of correlation depending on lead time before concatenation

dir = '/nird/projects/NS9873K/emile/heavy_files/'                                                           # The final array's size will be about 75MB, hence we store them outside of the git repo

lats = slice(62.5, 60.5)    # Hans area latitudes indexes
longs = slice(9, 11.75)     # Hans area longitudes indexes


###   Function

def process_file(data:xr.DataArray) -> None :
    global dataarrays
    data = data.sel(latitude=lats, longitude=longs)                                                         # Selecting hans' area
    fileDate = np.datetime64(key[1][-10:]).astype('datetime64[D]').astype(int)
    data['time'] = np.array([                                                                               # Reindex the lead times to have the length of the model
        (date.astype('datetime64[D]').astype(int) - fileDate) for date in data['time'].values
    ])
    data = data.reindex({"time":np.arange(15,46)})
    data = wd.pearson_correlation(data).to_dataset(dim="hdate")                                             # Compute the correlations statistics (norm, mean, std)
    for var in data.data_vars:
        dataarrays.append(data[var])
    data.close()


###   Processing

for key in tpSet.fileList:
    data = tpSet.open_data(key)
    process_file(data)

name = 's2s-hans_area-' + tpSet.resolution + '-correlation_statistics'
path = dir + name + '.nc'

res = xr.concat(dataarrays, dim="model")
res.name = "HA-correlation_statistics"
res.to_netcdf(path)
del dataarrays

tpSet.compute[name] = path

with open(wsPath, 'wb') as outp:
    pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)