""" Script to compute the maximum means """

import pickle

import weatherdata as wd



wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/continuous_0.25.pkl'
resDir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/'

with open(wsPath, 'rb') as inp:
    tpSet = pickle.load(inp)

name = 'continuous_max-mean2_' + tpSet.resolution + '_all-time'
if not name in tpSet.compute.keys():
    endPath = resDir + name + '.nc'
    tpSet.compute_time_max(meanSpan=2).to_netcdf(endPath)
    tpSet.compute[name] = endPath

name = 'continuous_max-mean3_' + tpSet.resolution + '_all-time'
if not name in tpSet.compute.keys():
    endPath = resDir + name + '.nc'
    tpSet.compute_time_max(meanSpan=3).to_netcdf(endPath)
    tpSet.compute[name] = endPath

name = 'continuous_max-mean2_' + tpSet.resolution + '_monthly'
if not name in tpSet.compute.keys():
    arraysList = []
    for m in range(1, 13):
        arr = tpSet.compute_time_max(months=[m], meanSpan=2)
        arr = arr.expand_dims({"time":[m]}).transpose("time", "latitude", "longitude")
        arraysList.append(arr)
        arr.close()
    endPath = resDir + name + '.nc'
    wd.xr.concat(arraysList, "time").to_netcdf(endPath)
    del arraysList
    tpSet.compute[name] = endPath

name = 'continuous_max-mean3_' + tpSet.resolution + '_monthly'
if not name in tpSet.compute.keys():
    arraysList = []
    for m in range(1, 13):
        arr = tpSet.compute_time_max(months=[m], meanSpan=3)
        arr = arr.expand_dims({"time":[m]}).transpose("time", "latitude", "longitude")
        arraysList.append(arr)
        arr.close()
    endPath = resDir + name + '.nc'
    wd.xr.concat(arraysList, "time").to_netcdf(endPath)
    del arraysList
    tpSet.compute[name] = endPath

name = 'continuous_max-mean2_' + tpSet.resolution + '_annual'
if not name in tpSet.compute.keys():
    arraysList = []
    for key in tpSet.fileList:
        data = wd.xr.open_dataarray(tpSet.pathsToFiles[key])
        arr = wd.xr.full_like(data, wd.np.nan)
        for i in range(len(arr['time'].values) - 1):
            arr[i, :, :] = data.isel(time=[i, i + 1]).mean(dim="time")
        arr = arr.max(dim="time")
        arr.expand_dims({"time":[key[1][-4:]]})
        arraysList.append(arr)
        arr.close()
        data.close()
    endPath = resDir + name + '.nc'
    wd.xr.concat(arraysList, "time").to_netcdf(endPath)
    del arraysList
    tpSet.compute[name] = endPath

name = 'continuous_max-mean3_' + tpSet.resolution + '_annual'
if not name in tpSet.compute.keys():
    arraysList = []
    for key in tpSet.fileList:
        data = wd.xr.open_dataarray(tpSet.pathsToFiles[key])
        arr = wd.xr.full_like(data, wd.np.nan)
        for i in range(1, len(arr['time'].values) - 1):
            arr[i, :, :] = data.isel(time=[i - 1, i, i + 1]).mean(dim="time")
        arr = arr.max(dim="time")
        arr.expand_dims({"time":[key[1][-4:]]})
        arraysList.append(arr)
        arr.close()
        data.close()
    endPath = resDir + name + '.nc'
    wd.xr.concat(arraysList, "time").to_netcdf(endPath)
    del arraysList
    tpSet.compute[name] = endPath

with open(wsPath, 'wb') as outp:
    pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)
