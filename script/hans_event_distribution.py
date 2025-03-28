""" Script to plot the mean on a large area each year and raise values over a certain threshold """

import xarray as xr
from weatherdata.classes import Weatherset

import pickle

wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/continuous_0.5.pkl'

with open(wsPath, 'rb') as inp:
    tpSet : Weatherset = pickle.load(inp)

name = 'continuous_hans-area-avg_' + tpSet.resolution + '_daily'

if not name in tpSet.compute.keys():

    latitudes = slice(62.5, 60.5)
    longitudes = slice(9, 11.75)

    alphaMonths = [
        "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec"
    ]

    values = []

    def process_daily(a:xr.DataArray) -> None :
        global values
        values.append(a.sel(latitude=latitudes, longitude=longitudes).mean(dim=["latitude","longitude"]))

    for key in tpSet.fileList:
        arr = tpSet.open_data(key)
        process_daily(arr)
        arr.close()
    
    path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/' + name + '.nc'

    xr.concat(values, dim="time").to_netcdf(path)

    tpSet.compute[name] = path

    with open(wsPath, 'wb') as outp:
        pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)