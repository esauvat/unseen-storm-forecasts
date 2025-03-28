""" Script to make the maps of maximum total precipitations ever modeled """

import pickle
import sys

import xarray as xr

import weatherdata as wd



wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/continuous_0.25.pkl'

with open(wsPath, 'rb') as inp:
    tpSet = pickle.load(inp)

mapDir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/maps/max/'
dataDir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/'


def all_time():
    """ Map with full resolution and time """
    global tpSet
    
    name = 'continuous_max_' + tpSet.resolution + '_all-time'
    title = "Maximum simulated precipitations"
    
    if name in tpSet.compute.keys():
        data = xr.open_dataarray(tpSet.compute[name])
        fig, _ = wd.functions.draw_map(data, title=title)
        fig.savefig(mapDir + 'tp24_' + tpSet.resolution + '_all-time.png')
    else:
        path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/' + name + '.nc'
        wd.functions.map_of_max(data=tpSet, title=title, dir=mapDir).to_netcdf(path)
        tpSet.compute[name] = path


def annual():
    """ Map with full resolution and annual maximum """
    global tpSet
    
    # 2019-2024
    name = 'continuous_max_' + tpSet.resolution + '_2019-2024'
    title = "Annual maximum simulated precipitations : 2019 - 2024"
    years = ['2019', '2020', '2021', '2022', '2023', '2024']
    
    if name in tpSet.compute.keys():
        data = xr.open_dataarray(tpSet.compute[name])
        fig, _ = wd.functions.draw_map(data, title=title, times=years)
        fig.savefig(mapDir + 'tp24_' + tpSet.resolution + '_2019-2024.png')
    else:
        path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/' + name + '.nc'
        wd.functions.map_of_max(data=tpSet, title=title, years=years, splitYears=True, dir=mapDir).to_netcdf(path)
        tpSet.compute[name] = path
        
        # 2013-2018
    name = 'continuous_max_' + tpSet.resolution + '_2013-2018'
    title = "Annual maximum simulated precipitations : 2013 - 2018"
    years = ['2013', '2014', '2015', '2016', '2017', '2018']
    
    if name in tpSet.compute.keys():
        data = xr.open_dataarray(tpSet.compute[name])
        fig, _ = wd.functions.draw_map(data, title=title, times=years)
        fig.savefig(mapDir + 'tp24_' + tpSet.resolution + '_2013-2018.png')
    else:
        path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/' + name + '.nc'
        wd.functions.map_of_max(data=tpSet, title=title, years=years, splitYears=True, dir=mapDir).to_netcdf(path)
        tpSet.compute[name] = path
        
        # 2007-2012
    name = 'continuous_max_' + tpSet.resolution + '_2007-2012'
    title = "Annual maximum simulated precipitations : 2007 - 2012"
    years = ['2007', '2008', '2009', '2010', '2011', '2012']
    
    if name in tpSet.compute.keys():
        data = xr.open_dataarray(tpSet.compute[name])
        fig, _ = wd.functions.draw_map(data, title=title, times=years)
        fig.savefig(mapDir + 'tp24_' + tpSet.resolution + '_2007-2012.png')
    else:
        path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/' + name + '.nc'
        wd.functions.map_of_max(data=tpSet, title=title, years=years, splitYears=True, dir=mapDir).to_netcdf(path)
        tpSet.compute[name] = path


def decadal():
    """ Map with full resolution and decadal maximum """
    
    name = 'continuous_max_' + tpSet.resolution + '_1941-2024-dec'
    title = "Decadal maximum simulated precipitations : 1941 - 2024"
    years = ['1940', '1950', '1960', '1970', '1980', '1990', '2000', '2010', '2020']
    sizeMap = 'large'
    
    if name in tpSet.compute.keys():
        data = xr.open_dataarray(tpSet.compute[name])
        fig, _ = wd.functions.draw_map(data, title=title, times=years, sizeMap=sizeMap)
        fig.savefig(mapDir + 'tp24_' + tpSet.resolution + '_1941-2024-dec.png')
    else:
        timeSpan = 10
        path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/' + name + '.nc'
        wd.functions.map_of_max(
            data=tpSet, title=title, years=years, splitYears=True, timeSpan=timeSpan, sizeMap=sizeMap, dir=mapDir
        ).to_netcdf(path)
        tpSet.compute[name] = path


def monthly():
    """ Map with full resolution and monthly maximum """
    
    global mapDir
    
    name = 'continuous_max_' + tpSet.resolution + '_monthly'
    title = "Monthly maximum recorded precipitations"
    months = [i for i in range(1, 13)]
    mapDir += 'monthly/'
    
    if name in tpSet.compute.keys():
        data = xr.open_dataarray(tpSet.compute[name])
        for month in months:
            alphaMonth = wd.alphaMonths[month]
            fig, _ = wd.functions.draw_map(data.sel(month=month), title=title + ' : ' + alphaMonth)
            fig.savefig(mapDir + 'tp24_' + tpSet.resolution + '_' + alphaMonth)
    else:
        path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/' + name + '.nc'
        wd.functions.map_of_max(data=tpSet, title=title, months=months, splitPlot=True, dir=mapDir).to_netcdf(path)
        tpSet.compute[name] = path


if __name__ == '__main__':
    func_name = sys.argv[1]
    globals()[func_name]()

with open(wsPath, 'wb') as outp:
    pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)
