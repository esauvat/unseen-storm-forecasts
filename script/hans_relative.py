""" Script to make the maps of report between Hans' data and maximum """

import pickle

import numpy as np
import xarray as xr

import weatherdata as wd



path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/continuous_0.25.pkl'
mapDir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/maps/hans_era5/'
dataDir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/results/'

with open(path, 'rb') as inp:
    tpSet = pickle.load(inp)

resolution = tpSet.resolution + 'x' + tpSet.resolution


def relative_august():
    global tpSet
    name = 'continuous_max_' + tpSet.resolution + '_monthly'
    
    if name in tpSet.compute.keys():
        data = xr.open_dataarray(tpSet.compute[name]).sel(time=8)
    else:
        title = "Monthly maximum recorded precipitations"
        data = wd.functions.map_of_max(data=tpSet, title=title, months=[i for i in range(1, 13)])
        maxPath = dataDir + name + '.nc'
        data.to_netcdf(maxPath)
        tpSet.compute[name] = maxPath
        data = data.sel(time=8)
    
    tp2023 = tpSet.open_data(key=('continuous', 'tp24_' + resolution + '_2023'))
    
    hansData = [tp2023.sel(time=np.datetime64('2023-08-06')),
                tp2023.sel(time=np.datetime64('2023-08-07')),
                tp2023.sel(time=np.datetime64('2023-08-08')),
                tp2023.sel(time=np.datetime64('2023-08-09'))]
    
    for dailyData in hansData:
        res = dailyData / data
        
        date = np.datetime_as_string(dailyData['time'].values)[:10]
        title = "Total precipitations relative to August's max : " + date
        fileName = "tp24_relative-max-august_all-res_" + date
        
        fig, axis = wd.functions.draw_map(res, title=title, extent=(0, 1))
        fig.savefig(mapDir + fileName + '.png')
        
        wd.geo.plt.close()
    
    hansMean2 = wd.mean_over_time(
        tp2023.sel(
            time=slice(
                np.datetime64('2023-08-07'),
                np.datetime64('2023-08-08')
            )
        ),
        2
    ).sel(time=np.datetime64('2023-08-08'))
    
    res = hansMean2 / data
    
    title = "Hans mean precipitations relative to August's max"
    fileName = "tp24_relative-max-august_all-res_hans-07-08"
    
    fig, axis = wd.functions.draw_map(res, title=title, extent=(0, 1))
    fig.savefig(mapDir + fileName + '.png')
    del hansMean2
    
    wd.geo.plt.close()
    
    hansMean3 = wd.mean_over_time(
        tp2023.sel(
            time=slice(
                np.datetime64('2023-08-07'),
                np.datetime64('2023-08-09')
            )
        ),
        3
    ).sel(time=np.datetime64('2023-08-08'))
    
    res = hansMean3 / data
    
    title = "Hans mean precipitations relative to August's max"
    fileName = "tp24_relative-max-august_all-res_hans-07-09"
    
    fig, axis = wd.functions.draw_map(res, title=title, extent=(0, 1))
    fig.savefig(mapDir + fileName + '.png')
    del hansMean3
    
    wd.geo.plt.close()
    
    hansMean4 = wd.mean_over_time(
        tp2023.sel(
            time=slice(
                np.datetime64('2023-08-06'),
                np.datetime64('2023-08-09')
            )
        ),
        4
    ).sel(time=np.datetime64('2023-08-08'))
    
    res = hansMean4 / data
    
    title = "Hans mean precipitations relative to August's max"
    fileName = "tp24_relative-max-august_all-res_hans-06-09"
    
    fig, axis = wd.functions.draw_map(res, title=title, extent=(0, 1))
    fig.savefig(mapDir + fileName + '.png')
    del hansMean4
    
    wd.geo.plt.close()


def relative_all_year():
    global tpSet
    name = 'continuous_max_' + tpSet.resolution + '_all-time'
    
    if name in tpSet.compute.keys():
        data = xr.open_dataarray(tpSet.compute[name])
    else:
        data = wd.functions.map_of_max(data=tpSet)
        maxPath = dataDir + name + '.nc'
        data.to_netcdf(maxPath)
        tpSet.compute[name] = maxPath
    
    tp2023 = tpSet.open_data(key=('continuous', 'tp24_' + resolution + '_2023'))
    
    hansData = [tp2023.sel(time=np.datetime64('2023-08-06')),
                tp2023.sel(time=np.datetime64('2023-08-07')),
                tp2023.sel(time=np.datetime64('2023-08-08')),
                tp2023.sel(time=np.datetime64('2023-08-09'))]
    
    for dailyData in hansData:
        res = dailyData / data
        res = res.drop_vars("time")
        date = np.datetime_as_string(dailyData['time'].values.astype('datetime64[D]'))
        
        title = "Total precipitations relative to yearly max : " + date
        fileName = "tp24_relative-max-year_all-res_" + date
        
        fig, axis = wd.functions.draw_map(res, title=title, extent=(0, 1))
        fig.savefig(mapDir + fileName + '.png')
        
        wd.geo.plt.close()
    
    hansMean2 = wd.mean_over_time(
        tp2023.sel(
            time=slice(
                np.datetime64('2023-08-07'),
                np.datetime64('2023-08-08')
            )
        ),
        2
    ).sel(time=np.datetime64('2023-08-08'))
    
    res = hansMean2 / data
    res = res.drop_vars("time")
    
    title = "Hans mean precipitations relative to yearly max"
    fileName = "tp24_relative-max-year_all-res_hans-07-08"
    
    fig, axis = wd.functions.draw_map(res, title=title, extent=(0, 1))
    fig.savefig(mapDir + fileName + '.png')
    del hansMean2
    
    wd.geo.plt.close()
    
    hansMean3 = wd.mean_over_time(
        tp2023.sel(
            time=slice(
                np.datetime64('2023-08-07'),
                np.datetime64('2023-08-09')
            )
        ),
        3
    ).sel(time=np.datetime64('2023-08-08'))
    
    res = hansMean3 / data
    res = res.drop_vars("time")
    
    title = "Hans mean precipitations relative to yearly max"
    fileName = "tp24_relative-max-year_all-res_hans-07-09"
    
    fig, axis = wd.functions.draw_map(res, title=title, extent=(0, 1))
    fig.savefig(mapDir + fileName + '.png')
    del hansMean3
    
    wd.geo.plt.close()
    
    hansMean4 = wd.mean_over_time(
        tp2023.sel(
            time=slice(
                np.datetime64('2023-08-06'),
                np.datetime64('2023-08-09')
            )
        ),
        4
    ).sel(time=np.datetime64('2023-08-08'))
    
    res = hansMean4 / data
    res = res.drop_vars("time")
    
    title = "Hans mean precipitations relative to yearly max"
    fileName = "tp24_relative-max-year_all-res_hans-06-09"
    
    fig, axis = wd.functions.draw_map(res, title=title, extent=(0, 1))
    fig.savefig(mapDir + fileName + '.png')
    del hansMean4
    
    wd.geo.plt.close()


def relative_mean2():
    global tpSet
    name = 'continuous_max-mean2_' + tpSet.resolution + '_all-time'
    
    assert name in tpSet.compute.keys()
    
    data = xr.open_dataarray(tpSet.compute[name])
    
    tp2023 = tpSet.open_data(key=('continuous', 'tp24_' + resolution + '_2023'))
    
    hansMean = wd.mean_over_time(
        tp2023.sel(
            time=slice(
                np.datetime64('2023-08-07'),
                np.datetime64('2023-08-08')
            )
        ),
        2
    ).sel(time=np.datetime64('2023-08-08'))
    
    res = hansMean / data
    res = res.drop_vars("time")
    
    title = "Hans mean precipitations relative to yearly mean maximum"
    fileName = "tp24_relative-mean-max-year_0.25_hans-07-08"
    
    fig, axis = wd.functions.draw_map(res, title=title, extent=(0, 1))
    fig.savefig(mapDir + fileName + '.png')
    del hansMean
    
    wd.geo.plt.close()


def relative_mean3():
    global tpSet
    name = 'continuous_max-mean3_0.25_all-time'
    
    assert name in tpSet.compute.keys()
    
    data = xr.open_dataarray(tpSet.compute[name])
    
    tp2023 = tpSet.open_data(key=('continuous', 'tp24_' + resolution + '_2023'))
    
    hansMean = wd.mean_over_time(
        tp2023.sel(
            time=slice(
                np.datetime64('2023-08-07'),
                np.datetime64('2023-08-09')
            )
        ),
        3
    ).sel(time=np.datetime64('2023-08-08'))
    
    res = hansMean / data
    res = res.drop_vars("time")
    
    title = "Hans mean precipitations relative to yearly mean maximum"
    fileName = "tp24_relative-mean-max-year_0.25_hans-07-09"
    
    fig, axis = wd.functions.draw_map(res, title=title, extent=(0, 1))
    fig.savefig(mapDir + fileName + '.png')
    del hansMean
    
    wd.geo.plt.close()


def relative_mean2_monthly():
    global tpSet
    name = 'continuous_max-mean2_0.25_monthly'
    
    assert name in tpSet.compute.keys()
    
    data = xr.open_dataarray(tpSet.compute[name])
    
    tp2023 = tpSet.open_data(key=('continuous', 'tp24_' + resolution + '_2023'))
    
    hansMean = wd.mean_over_time(
        tp2023.sel(
            time=slice(
                np.datetime64('2023-08-07'),
                np.datetime64('2023-08-08')
            )
        ),
        2
    ).sel(time=np.datetime64('2023-08-08'))
    
    res = hansMean / data
    
    title = "Hans mean precipitations relative to August's mean maximum"
    fileName = "tp24_relative-mean-max-august_0.25_hans-07-08"
    
    fig, axis = wd.functions.draw_map(res, title=title, extent=(0, 1))
    fig.savefig(mapDir + fileName + '.png')
    del hansMean
    
    wd.geo.plt.close()


def relative_mean3_monthly():
    global tpSet
    name = 'continuous_max-mean3_0.25_monthly'
    
    assert name in tpSet.compute.keys()
    
    data = xr.open_dataarray(tpSet.compute[name])
    
    tp2023 = tpSet.open_data(key=('continuous', 'tp24_' + resolution + '_2023'))
    
    hansMean = wd.mean_over_time(
        tp2023.sel(
            time=slice(
                np.datetime64('2023-08-07'),
                np.datetime64('2023-08-09')
            )
        ),
        3
    ).sel(time=np.datetime64('2023-08-08'))
    
    res = hansMean / data
    
    title = "Hans mean precipitations relative to August's mean maximum"
    fileName = "tp24_relative-mean-max-august_0.25_hans-07-09"
    
    fig, axis = wd.functions.draw_map(res, title=title, extent=(0, 1))
    fig.savefig(mapDir + fileName + '.png')
    del hansMean
    
    wd.geo.plt.close()


with open(path, 'wb') as outp:
    pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)
