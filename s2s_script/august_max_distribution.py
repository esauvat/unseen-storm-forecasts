
''' Compute the distribution of august's maximum '''

import sys

sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/python_mapping/')

import numpy as np, xarray as xr, pandas as pd
import weatherdata as wd
import pickle


###   Opening the Weatherset

wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_0.5.pkl'

with open(wsPath, 'rb') as inp:
    tpSet = pickle.load(inp)


###   Variables

latitudes = slice(62.5, 60.5)
longitudes = slice(9, 11.75)

dataDir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results'

###   Defining utility functions

def select_aug(month:int) -> bool:
    return month == 8


def process_file(tpSet:wd.Weatherset, key:str, span:int|None=1) -> xr.DataArray :
    if not key in tpSet.fileList:
        return None, None
    arr = tpSet.open_data(key)
    arr = arr.sel(latitude=latitudes, longitude=longitudes)                                         # Selecting the geographic area
    timeRange = 7 + span - 1
    arr = arr.isel(time=slice(timeRange, 45))                                                       # Selecting the time range (1 week plus the edges to make the sum)
    if span > 1 :
        arr = arr.rolling(time=span, min_periods=span).mean().isel(time=slice(-7,45))
    return arr.sel(time=select_aug(arr['time.month'])).max(dim="time"), key


def date_as_float(date:np.datetime64) -> float :
    obj = date.astype(object)
    return obj.month + obj.day/100


def test_time(fileName:str, nbWeeks:int|None=1, timeRange:tuple[float, float]|None=(8.01,8.31)) -> bool:
    fileDate = np.datetime64(fileName[-10:])
    endDate = fileDate + np.timedelta64(45, 'D')
    startDate = endDate - np.timedelta64(7*nbWeeks, 'D')
    return (date_as_float(startDate)<=timeRange[1]) and (date_as_float(endDate)>=timeRange[0])


def compute_distrib(tpSet:wd.Weatherset, span:int|None=1) -> xr.DataArray:
    dataarrays = []
    fileNames = np.unique([fileName for _,fileName in tpSet.fileList])
    for fileName in fileNames:
        if test_time(fileName) :
            fKey = ('forecast', fileName)
            hKey = ('hindcast', fileName)
            forecast, fKey = process_file(tpSet, fKey, span)
            hindcast, hKey = process_file(tpSet, hKey, span)
            if fKey and hKey:
                arr = xr.concat([forecast, hindcast], dim="hdate")
                forecast.close()
                hindcast.close()
            elif fKey:
                arr = forecast.copy()
                forecast.close()
            else:
                arr = hindcast.copy()
                hindcast.close()
            fArr = arr.expand_dims({"name":[fileName]}).reindex({"number":np.arange(1,52)}, copy=True)
            dataarrays.append(arr)
            arr.close()
            fArr.close()
    res = xr.concat(dataarrays, dim="name")
    del dataarrays
    return res


###   Processing

names = ['s2s-hans_area-' + tpSet.resolution + '-aug_daily_max',
         's2s-hans_area-' + tpSet.resolution + '-aug_mean2_max',
         's2s-hans_area-' + tpSet.resolution + '-aug_mean3_max']

for nameIdx, name in enumerate(names):
    if not name in tpSet.compute.keys():
        maxArr = compute_distrib(tpSet, nameIdx+1)
        path = dataDir + name + '.nc'
        maxArr.to_netcdf(path)
        tpSet.compute[name] = path