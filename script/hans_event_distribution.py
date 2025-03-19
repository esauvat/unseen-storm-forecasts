
''' Script to plot the mean on a large area each year and raise values over a certain threshold '''

import sys

sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/python_mapping')
sys.path.append('/home/esauvat/Documents/NORCE/unseen-storm-forecasts/python_mapping')

import weatherdata
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

import pickle

with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/continuous_0.25.pkl', 'rb') as inp:
    tpSet = pickle.load(inp)


latitudes = slice(62.5, 60.5)
longitudes = slice(9, 11.75)

alphaMonths = [
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec"
]

data = dict()

def process_daily(arr:xr.DataArray) -> None :
    global data
    for time in arr['time'].values:
        value = arr.sel(
            time=time, 
            latitude=latitudes, 
            longitude=longitudes).mean()
        data[time] = np.float32(value)

for key in tpSet.fileList:
    arr = xr.open_dataarray(tpSet.pathsToFiles[key])
    process_daily(arr)
    arr.close()

dailyValues = dict(
    jan=[], feb=[], mar=[], apr=[], may=[], jun=[],
    jul=[], aug=[], sep=[], oct=[], nov=[], dec=[]
)

mean2Values = dict(
    jan=[], feb=[], mar=[], apr=[], may=[], jun=[],
    jul=[], aug=[], sep=[], oct=[], nov=[], dec=[]
)

mean3Values = dict(
    jan=[], feb=[], mar=[], apr=[], may=[], jun=[],
    jul=[], aug=[], sep=[], oct=[], nov=[], dec=[]
)


dailyValues['dec'].append(
    (data[np.datetime64('2024-12-31')],
     '2024-12-31')
)

dailyValues['jan'].append(
    (data[np.datetime64('1941-01-01')],
     '1941-01-01')
)

mean2Values['jan'].append(
    ((data[np.datetime64('1941-01-01')]+data[np.datetime64('1941-01-02')])/2,
     '1941-01-01')
)

for date in np.arange(np.datetime64('1941-01-02'), np.datetime64('2024-12-31'), np.timedelta64(1, 'D')):
    month = alphaMonths[date.astype('datetime64[M]').astype(int) % 12]
    dailyValues[month].append((data[date], np.datetime_as_string(date)))
    mean2 = ( data[date] + data[date+np.timedelta64(1,'D')] ) / 2
    mean2Values[month].append((mean2, np.datetime_as_string(date)))
    mean3 = ( data[date-np.timedelta64(1,'D')] + data[date] + data[date+np.timedelta64(1,'D')] ) / 3
    mean3Values[month].append((mean3, np.datetime_as_string(date)))


with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/continuous_hans-area-avg_0.25_daily.pkl', 'wb') as outp:
    pickle.dump(data, outp, pickle.HIGHEST_PROTOCOL)

with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/continuous_hans-area-avg-daily_0.25_monthly.pkl', 'wb') as outp:
    pickle.dump(dailyValues, outp, pickle.HIGHEST_PROTOCOL)

with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/continuous_hans-area-avg-mean2_0.25_monthly.pkl', 'wb') as outp:
    pickle.dump(mean2Values, outp, pickle.HIGHEST_PROTOCOL)

with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/continuous_hans-area-avg-mean3_0.25_monthly.pkl', 'wb') as outp:
    pickle.dump(mean3Values, outp, pickle.HIGHEST_PROTOCOL)