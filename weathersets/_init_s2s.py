""" Creation of s2s weathersets """

import pickle

from weatherdata.classes import Weatherset



###   Setting variables

dirs = [
    '/nird/projects/NS9873K/etdu/processed/cf-forsikring/s2s/ecmwf/forecast/daily/values/tp24/',
    '/nird/projects/NS9873K/etdu/processed/cf-forsikring/s2s/ecmwf/hindcast/daily/values/tp24/' ]

###   Creation of the datasets

hRes = Weatherset(
    dirs, reanalysis=False, resolution='0.25', multiType=True,
    resultsDirectory='/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/'
)
lRes = Weatherset(
    dirs, reanalysis=False, resolution='0.5', multiType=True,
    resultsDirectory='/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/'
)
allRes = Weatherset(
    dirs, reanalysis=False, multiType=True,
    resultsDirectory='/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/'
)

lResHindcast = Weatherset(
    [dirs[1]], reanalysis=False, resolution='0.5',
    resultsDirectory='/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/hindcast_results/'
)
hResHindcast = Weatherset(
    [dirs[1]], reanalysis=False, resolution='0.25',
    resultsDirectory='/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/hindcast_results/'
)
allResHindcast = Weatherset(
    [dirs[1]], reanalysis=False,
    resultsDirectory='/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/hindcast_results/'
)

lResForecast = Weatherset(
    [dirs[0]], reanalysis=False, resolution='0.5',
    resultsDirectory='/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/forecast_results/'
)
hResForecast = Weatherset(
    [dirs[0]], reanalysis=False, resolution='0.25',
    resultsDirectory='/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/forecast_results/'
)
allResForecast = Weatherset(
    [dirs[0]], reanalysis=False,
    resultsDirectory='/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/forecast_results/'
)

###   Saving

with open('s2s_0.25.pkl', 'wb') as outp:
    pickle.dump(hRes, outp, pickle.HIGHEST_PROTOCOL)
with open('s2s_0.5.pkl', 'wb') as outp:
    pickle.dump(lRes, outp, pickle.HIGHEST_PROTOCOL)
with open('s2s_all-res.pkl', 'wb') as outp:
    pickle.dump(allRes, outp, pickle.HIGHEST_PROTOCOL)

with open('s2s_0.25_hindcast.pkl', 'wb') as outp:
    pickle.dump(hResHindcast, outp, pickle.HIGHEST_PROTOCOL)
with open('s2s_0.5_hindcast.pkl', 'wb') as outp:
    pickle.dump(lResHindcast, outp, pickle.HIGHEST_PROTOCOL)
with open('s2s_all-res_hindcast.pkl', 'wb') as outp:
    pickle.dump(allResHindcast, outp, pickle.HIGHEST_PROTOCOL)

with open('s2s_0.25_forecast.pkl', 'wb') as outp:
    pickle.dump(hResForecast, outp, pickle.HIGHEST_PROTOCOL)
with open('s2s_0.5_forecast.pkl', 'wb') as outp:
    pickle.dump(lResForecast, outp, pickle.HIGHEST_PROTOCOL)
with open('s2s_all-res_forecast.pkl', 'wb') as outp:
    pickle.dump(allResForecast, outp, pickle.HIGHEST_PROTOCOL)
