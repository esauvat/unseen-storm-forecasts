
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

wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_all-res.pkl'

""" with open(wsPath, 'rb') as inp:
    tpSet = pickle.load(inp) """

# Just for this time :
directories = ['/nird/projects/NS9873K/etdu/processed/cf-forsikring/s2s/ecmwf/forecast/daily/values/tp24/',
               '/nird/projects/NS9873K/etdu/processed/cf-forsikring/s2s/ecmwf/hindcast/daily/values/tp24/']
tpSet = wd.Weatherset(directories, reanalysis=False, multiType=True)


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
span = dictType[argType]


###   Function

def process_files(keys:list[tuple], fileDate:int, tpSet:wd.Weatherset) -> None :
    global dataarrays
    datas = [tpSet.open_data(key).sel(latitude=lats,longitude=longs).mean(dim=["latitude","longitude"]) 
             for key in keys]
    data = xr.concat([
        xr.concat(datas[:2], dim="time"),
        xr.concat(datas[2:], dim="time")
    ], dim="hdate")
    del datas
    if span:
        data = wd.mean_over_time(data, span, False)
    fileDate = np.datetime64(fileDate).astype('datetime64[D]').astype(int)
    data['time'] = np.array([
        (date.astype('datetime64[D]').astype(int) - fileDate) for date in data['time'].values
    ])
    data = xr.apply_ufunc(
        wd.pears, data,
        input_core_dims=[["number"]],
        output_core_dims=[[]],
        vectorize=True
    )
    for hdate in data['hdate'].values:
        dataarrays.append(data.sel(hdate=hdate))
    data.close()


###   Processing

fileDates = np.unique([fileName[-10:] for _,fileName in tpSet.fileList])
fileDates = fileDates[np.where(fileDates <= '2022-12-29')]

hResName = 'tp24_0.25x0.25_'
lResName = 'tp24_0.5x0.5_'

for date in fileDates:
    keys = [('forecast', hResName+date),
            ('forecast', lResName+date),
            ('hindcast', hResName+date),
            ('hindcast', lResName+date)]
    if np.any([not (key in tpSet.fileList) for key in keys]):
        raise "The dataset is uncomplete"
    else:
        process_files(keys, date, tpSet)

name = 's2s-hans_area-' + tpSet.resolution + '-' + argType + '_correlation'
path = dir + name + '.nc'

res = xr.concat(dataarrays, dim="date", )
del dataarrays
res.name = "correl-HA_avg"
res.to_netcdf(path)

tpSet.compute[name] = path

with open(wsPath, 'wb') as outp:
    pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)