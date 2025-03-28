
''' We want to compute the correlation between ensemble members in the mean over Hans' area. Since for a specific lead
time, the ensemble member carry only one value, we can rather simply compute the total correlatio between all of the ensemble 
members. This will be much harder when handling all the grid. We will probably start by computing the correlation matrix. '''


###   Packages 

import sys
import weatherdata as wd
import numpy as np, xarray as xr
import pickle


###   Opening the dataset

wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_all-res.pkl'

with open(wsPath, 'rb') as inp:
    tpSet = pickle.load(inp)


###   Variables

arraysList = []

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

def process_files(keys:list[tuple], fileDate:str, tpSet:wd.Weatherset) -> None :
    global arraysList
    
    forecast = xr.concat(
        [xr.open_dataarray(tpSet.pathsToFiles[keys[0]]).sel(latitude=lats,longitude=longs).mean(["latitude","longitude"]),
        xr.open_dataarray(tpSet.pathsToFiles[keys[1]]).sel(latitude=lats,longitude=longs).mean(["latitude","longitude"])],
        dim="time"
    ).expand_dims({"hdate":[int("".join(fileDate.split('-')))]})
    hindcast = xr.concat(
        [xr.open_dataarray(tpSet.pathsToFiles[keys[2]]).sel(latitude=lats,longitude=longs).mean(["latitude","longitude"]),
        xr.open_dataarray(tpSet.pathsToFiles[keys[3]]).sel(latitude=lats,longitude=longs).mean(["latitude","longitude"])],
        dim="time"
    )
    data = xr.concat([
        forecast, 
        hindcast], 
        dim="hdate"
    )
    forecast.close()
    hindcast.close()

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

if tpSet.resolution:
    resolution = tpSet.resolution
else:
    resolution = 'all_res'

name = 's2s-HA_avg_correlation-' + resolution + '-' + argType
path = dir + name + '.nc'

res = xr.concat(arraysList, dim="date")
del arraysList
res.name = "correl-HA_avg"
res.to_netcdf(path)

tpSet.compute[name] = path

with open(wsPath, 'wb') as outp:
    pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)