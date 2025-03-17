
''' Script to compute the maximum means '''

import sys

sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/python_mapping')

import weatherdata as wd
import pickle

path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/continuous_0.25.pkl'
dir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/results/'

with open(path, 'rb') as inp:
    tpSet = pickle.load(inp)

name = 'continuous_max-mean2_0.25_all-time'
if not name in tpSet.compute.keys():
    res = tpSet.compute_time_max(meanSpan = 2)
    endPath = dir + name + '.pkl'
    with open(endPath, 'wb') as outp:
        pickle.dump(res, outp, pickle.HIGHEST_PROTOCOL)
        tpSet.compute[name] = endPath

name = 'continuous_max-mean3_0.25_all-time'
if not name in tpSet.compute.keys():
    res = tpSet.compute_time_max(meanSpan = 3)
    endPath = dir + name + '.pkl'
    with open(endPath, 'wb') as outp:
        pickle.dump(res, outp, pickle.HIGHEST_PROTOCOL)
        tpSet.compute[name] = endPath

name = 'continuous_max-mean2_0.25_monthly'
if not name in tpSet.compute.keys():
    dataarrays = []
    for m in range(1, 13):
        arr = tpSet.compute_time_max(months=[m], meanSpan = 2)
        arr = arr.expand_dims({"time":[m]}).transpose("time","latitude","longitude")
        dataarrays.append(arr)
        arr.close()
    res = wd.xr.concat(dataarrays, "time")
    del dataarrays
    endPath = dir + name + '.pkl'
    with open(endPath, 'wb') as outp:
        pickle.dump(res, outp, pickle.HIGHEST_PROTOCOL)
        tpSet.compute[name] = endPath

name = 'continuous_max-mean3_0.25_monthly'
if not name in tpSet.compute.keys():
    dataarrays = []
    for m in range(1, 13):
        arr = tpSet.compute_time_max(months=[m], meanSpan = 3)
        arr = arr.expand_dims({"time":[m]}).transpose("time","latitude","longitude")
        dataarrays.append(arr)
        arr.close()
    res = wd.xr.concat(dataarrays, "time")
    del dataarrays
    endPath = dir + name + '.pkl'
    with open(endPath, 'wb') as outp:
        pickle.dump(res, outp, pickle.HIGHEST_PROTOCOL)
        tpSet.compute[name] = endPath


with open(path, 'wb') as outp:
    pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)