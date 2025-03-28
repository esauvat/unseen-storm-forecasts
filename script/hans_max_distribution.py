
''' Script to plot the mean maximum on a large area each year and raise values over a certain threshold '''

import numpy as np
import xarray as xr
import weatherdata as wd

import pickle

wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/continuous_0.5.pkl'

with open(wsPath, 'rb') as inp:
    tpSet = pickle.load(inp)

data = xr.open_dataarray(tpSet.compute['continuous_hans-area-avg_'+tpSet.resolution+'_daily'])

dir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/'

alphaMonths = np.array([
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec"
])

years = np.arange(np.datetime64('1941'), np.datetime64('2025')).astype(str)

def sort_monthly_max(data:xr.DataArray):
    ''' Get the maximum for each month '''
    months = np.arange(np.datetime64('1941'), np.datetime64('2025'), np.timedelta64(1,'M'))
    res = xr.DataArray(
        np.full((len(alphaMonths), len(years)), None), 
        dims = ("months", "years"),
        coords = {"months":alphaMonths, "years":years}
    )
    for m in months:
        mIdx = m.astype(int) % 12
        yIdx = int(np.datetime_as_string(m)[:4]) - 1941
        val = data.sel(time=slice(m, m+np.timedelta64(1,'M')-np.timedelta64(1,'D'))).max()
        res[mIdx, yIdx] = val
    return res


dailyName = 'continuous_hans-area-avg-daily_'+tpSet.resolution+'_monthly-max'
mean2Name = 'continuous_hans-area-avg-mean2_'+tpSet.resolution+'_monthly-max'
mean3Name = 'continuous_hans-area-avg-mean3_'+tpSet.resolution+'_monthly-max'

if not dailyName in tpSet.compute.keys():
    path = dir+dailyName
    sort_monthly_max(data).to_netcdf(path)
    tpSet.compute[dailyName] = path

if not mean2Name in tpSet.compute.keys():
    path = dir+mean2Name
    mean2 = wd.mean_over_time(data=data, span=2, edges=False)
    sort_monthly_max(mean2).to_netcdf(path)
    tpSet.compute[mean2Name] = path

if not mean3Name in tpSet.compute.keys():
    path = dir+mean3Name
    mean3 = wd.mean_over_time(data=data, span=3, edges=False)
    sort_monthly_max(mean3).to_netcdf(path)
    tpSet.compute[mean3Name] = path


with open(wsPath, 'wb') as outp:
    pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)