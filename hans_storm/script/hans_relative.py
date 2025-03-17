
''' Script to make the maps of report between Hans' data and maximum '''

import sys

sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/python_mapping')

import weatherdata as wd
import pickle

path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/continuous_all-res.pkl'


with open(path, 'rb') as inp:
    tpSet = pickle.load(inp)

def relative_august():
    name = 'continuous_max_all-res_monthly'

    if name in tpSet.compute.keys():
        with open(tpSet.compute[name], 'rb') as inp:
            data = pickle.load(inp).sel(time=8)
            data = pickle.load(inp)
    else:
        title = "Monthly maximum recorded precipitations"
        data = wd.map_of_max(data=tpSet, title=title, months=[i for i in range(1, 13)])
        maxPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/results/continuous_max_all-res_monthly.pkl'
        with open(maxPath, 'wb') as outp:
            pickle.dump(data, outp, pickle.HIGHEST_PROTOCOL)
            tpSet.compute[name] = maxPath
        data = data.sel(time=8)

    if tpSet.resolution == '0.5':
        resolution = '0.5x0.5'
    else:
        resolution = '0.25x0.25'

    tp2023 = tpSet.open_data(key=('continuous','tp24_'+resolution+'_2023'))

    hansData = [tp2023.sel(time=wd.np.datetime64('2023-08-06')),
                tp2023.sel(time=wd.np.datetime64('2023-08-07')),
                tp2023.sel(time=wd.np.datetime64('2023-08-08')),
                tp2023.sel(time=wd.np.datetime64('2023-08-09'))]

    endDir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/maps/hans_era5/'

    for dailyData in hansData:
        res = dailyData / data
        date = wd.np.datetime_as_string(dailyData['time'].values)[:10]
        title = "Total precipitations relative to August's max : " + date
        fileName = "tp24_relative-max-august_all-res_" + date
        fig, axis = wd.draw_map(res, title=title, extent=(0,1))
        fig.savefig(endDir+fileName+'.png')
        wd.geo.plt.close()

    hansMean2 = wd.mean_over_time(
        tp2023.sel(time=slice(
            wd.np.datetime64('2023-08-07'),
            wd.np.datetime64('2023-08-08')
        )), 
        2).sel(time=wd.np.datetime64('2023-08-08'))

    res = hansMean2 / data
    title = "Hans mean precipitations relative to August's max"
    fileName = "tp24_relative-max-august_all-res_hans-07-08"
    fig, axis = wd.draw_map(res, title=title, extent=(0,1))
    fig.savefig(endDir+fileName+'.png')
    del hansMean2
    wd.geo.plt.close()

    hansMean3 = wd.mean_over_time(
        tp2023.sel(time=slice(
            wd.np.datetime64('2023-08-07'),
            wd.np.datetime64('2023-08-09')
        )), 
        3).sel(time=wd.np.datetime64('2023-08-08'))

    res = hansMean3 / data
    title = "Hans mean precipitations relative to August's max"
    fileName = "tp24_relative-max-august_all-res_hans-07-09"
    fig, axis = wd.draw_map(res, title=title, extent=(0,1))
    fig.savefig(endDir+fileName+'.png')
    del hansMean3
    wd.geo.plt.close()

    hansMean4 = wd.mean_over_time(
        tp2023.sel(time=slice(
            wd.np.datetime64('2023-08-06'),
            wd.np.datetime64('2023-08-09')
        )), 
        4).sel(time=wd.np.datetime64('2023-08-08'))

    res = hansMean4 / data
    title = "Hans mean precipitations relative to August's max"
    fileName = "tp24_relative-max-august_all-res_hans-06-09"
    fig, axis = wd.draw_map(res, title=title, extent=(0,1))
    fig.savefig(endDir+fileName+'.png')
    del hansMean4
    wd.geo.plt.close()



def relative_all_year():
    name = 'continuous_max_all-res_all-time'

    if name in tpSet.compute.keys():
        with open(tpSet.compute[name], 'rb') as inp:
            data = pickle.load(inp)
    else:
        data = wd.map_of_max(data=tpSet)
        maxPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/results/continuous_max_all-res_all-time.pkl'
        with open(maxPath, 'wb') as outp:
            pickle.dump(data, outp, pickle.HIGHEST_PROTOCOL)
            tpSet.compute[name] = maxPath

    if tpSet.resolution == '0.5':
        resolution = '0.5x0.5'
    else:
        resolution = '0.25x0.25'

    tp2023 = tpSet.open_data(key=('continuous','tp24_'+resolution+'_2023'))

    hansData = [tp2023.sel(time=wd.np.datetime64('2023-08-06')),
                tp2023.sel(time=wd.np.datetime64('2023-08-07')),
                tp2023.sel(time=wd.np.datetime64('2023-08-08')),
                tp2023.sel(time=wd.np.datetime64('2023-08-09'))]

    endDir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/maps/hans_era5/'

    for dailyData in hansData:
        res = dailyData / data
        res = res.drop_vars("time")
        date = wd.np.datetime_as_string(dailyData['time'].values)[:10]
        title = "Total precipitations relative to yearly max : " + date
        fileName = "tp24_relative-max-year_all-res_" + date
        fig, axis = wd.draw_map(res, title=title, extent=(0,1))
        fig.savefig(endDir+fileName+'.png')
        wd.geo.plt.close()

    hansMean2 = wd.mean_over_time(
        tp2023.sel(time=slice(
            wd.np.datetime64('2023-08-07'),
            wd.np.datetime64('2023-08-08')
        )), 
        2).sel(time=wd.np.datetime64('2023-08-08'))

    res = hansMean2 / data
    res = res.drop_vars("time")
    title = "Hans mean precipitations relative to yearly max"
    fileName = "tp24_relative-max-year_all-res_hans-07-08"
    fig, axis = wd.draw_map(res, title=title, extent=(0,1))
    fig.savefig(endDir+fileName+'.png')
    del hansMean2
    wd.geo.plt.close()

    hansMean3 = wd.mean_over_time(
        tp2023.sel(time=slice(
            wd.np.datetime64('2023-08-07'),
            wd.np.datetime64('2023-08-09')
        )), 
        3).sel(time=wd.np.datetime64('2023-08-08'))

    res = hansMean3 / data
    res = res.drop_vars("time")
    title = "Hans mean precipitations relative to yearly max"
    fileName = "tp24_relative-max-year_all-res_hans-07-09"
    fig, axis = wd.draw_map(res, title=title, extent=(0,1))
    fig.savefig(endDir+fileName+'.png')
    del hansMean3
    wd.geo.plt.close()

    hansMean4 = wd.mean_over_time(
        tp2023.sel(time=slice(
            wd.np.datetime64('2023-08-06'),
            wd.np.datetime64('2023-08-09')
        )), 
        4).sel(time=wd.np.datetime64('2023-08-08'))

    res = hansMean4 / data
    res = res.drop_vars("time")
    title = "Hans mean precipitations relative to yearly max"
    fileName = "tp24_relative-max-year_all-res_hans-06-09"
    fig, axis = wd.draw_map(res, title=title, extent=(0,1))
    fig.savefig(endDir+fileName+'.png')
    del hansMean4
    wd.geo.plt.close()



if __name__=='__main__':
    func_name = sys.argv[1]
    globals()[func_name]()