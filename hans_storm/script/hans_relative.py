
''' Script to make the maps of report between Hans' data and maximum '''

import sys

sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/python_mapping')

import weatherdata as wd
import pickle

path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/continuous_all-res.pkl'


with open(path, 'rb') as inp:
    tpSet = pickle.load(inp)

name = 'continuous_max_all-res_monthly'
nameAugust = 'continuous_max_all-res_August'

if name in tpSet.compute.keys():
    with open(tpSet.compute[name], 'rb') as inp:
        data = pickle.load(inp).sel(time=8)
elif nameAugust in tpSet.compute.keys():
    with open(tpSet.compute[nameAugust], 'rb') as inp:
        data = pickle.load(inp)
else:
    title = "August maximum recorded precipitations"
    data = wd.map_of_max(data=tpSet, title=title, months=[8])
    augustPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/results/continuous_max_all-res_August.pkl'
    with open(augustPath, 'wb') as outp:
        pickle.dump(data, outp, pickle.HIGHEST_PROTOCOL)
        tpSet.compute[nameAugust] = augustPath

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
wd.geo.plt.close()