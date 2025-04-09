""" Script to plot the mean on a large area each year and raise values
over a certain threshold """

import pickle

import xarray as xr

from weatherdata.classes import Weatherset
from weatherdata.geographics import apply_curv_weights



wsPath = ('/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets'
          '/continuous_0.5.pkl')

with open(wsPath, 'rb') as inp:
    tpSet: Weatherset = pickle.load(inp)

name = 'continuous_hans-area-avg_' + tpSet.resolution + '_daily'

if not name in tpSet.compute.keys():
    
    latitudes = slice(62.5, 60.5)
    longitudes = slice(9, 11.75)
    
    alphaMonths = [
        "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug",
        "sep", "oct", "nov", "dec"]
    
    values = []
    
    
    def process_daily(a: xr.DataArray) -> None:
        global values
        a = apply_curv_weights(a.sel(
            latitude=latitudes, longitude=longitudes
        ))
        values.append(
            a.mean(
                dim=["latitude", "longitude"]
            )
        )
    
    
    for key in tpSet.fileList:
        arr = tpSet.open_data(key)
        process_daily(arr)
        arr.close()
    
    path = ('/nird/projects/NS9873K/emile/unseen-storm-forecasts'
            '/weathersets/results/') + name + '.nc'
    
    xr.concat(values, dim="time").to_netcdf(path)
    
    tpSet.compute[name] = path
    
    with open(wsPath, 'wb') as outp:
        pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)
