
''' Script to plot the mean maximum on a large area each year and raise values over a certain threshold '''

import sys

sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/python_mapping')
sys.path.append('/home/esauvat/Documents/NORCE/unseen-storm-forecasts/python_mapping')

import numpy as np

import pickle

with open('/home/esauvat/Documents/NORCE/unseen-storm-forecasts/hans_storm/data/weathersets/results/continuous_hans-area-avg_0.25_daily.pkl', 'rb') as inp:
    data = pickle.load(inp)

alphaMonths = [
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec"
]


def sort_monthly_max(data:dict, res:dict):
    for year in np.arange(np.datetime64('1941'), np.datetime64('2025'), np.timedelta64(1, 'Y')):
        for month in np.arange(year, year+np.timedelta64(1,'Y'), np.timedelta64(1, 'M')):
            vals = np.array(
                [data[day] for day in np.arange(
                    month, 
                    month+np.timedelta64(1,'M'), 
                    np.timedelta64(1,'D')
                )]
            )
            monthIdx = alphaMonths[month.astype(int) % 12]
            res[monthIdx].append((vals.max(), 
                                  np.datetime_as_string(year)))

mean2 = {np.datetime64('2024-12-31'):np.nan}

for day in np.arange(np.datetime64('1941'), np.datetime64('2024-12-31'), np.timedelta64(1, 'D')):
    val = ( data[day] + data[day+np.timedelta64(1,'D')] ) / 2
    mean2[day] = val

mean3 = {np.datetime64('1941-01-01'):np.nan,
         np.datetime64('2024-12-31'):np.nan}

for day in np.arange(np.datetime64('1941-01-02'), np.datetime64('2024-12-31'), np.timedelta64(1,'D')):
    val = ( data[day-np.timedelta64(1,'D')] + data[day] + data[day+np.timedelta64(1,'D')] ) / 3
    mean3[day] = val

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

sort_monthly_max(data, dailyValues)
sort_monthly_max(mean2, mean2Values)
sort_monthly_max(mean3, mean3Values)

with open('/home/esauvat/Documents/NORCE/unseen-storm-forecasts/hans_storm/data/weathersets/results/continuous_hans-area-avg-daily_0.25_monthly-max.pkl', 'wb') as outp:
    pickle.dump(dailyValues, outp, pickle.HIGHEST_PROTOCOL)

with open('/home/esauvat/Documents/NORCE/unseen-storm-forecasts/hans_storm/data/weathersets/results/continuous_hans-area-avg-mean2_0.25_monthly-max.pkl', 'wb') as outp:
    pickle.dump(mean2Values, outp, pickle.HIGHEST_PROTOCOL)

with open('/home/esauvat/Documents/NORCE/unseen-storm-forecasts/hans_storm/data/weathersets/results/continuous_hans-area-avg-mean3_0.25_monthly-max.pkl', 'wb') as outp:
    pickle.dump(mean3Values, outp, pickle.HIGHEST_PROTOCOL)