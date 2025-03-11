
''' Script to make the maps of maximum total precipitations ever modeled '''

import sys

sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/python_mapping')

import weatherdata as wd

dir1 = '/nird/projects/NS9873K/etdu/processed/cf-forsiking/era5/continuous-format/daily/tp24'
dir2 = '/nird/projects/NS9873K/etdu/processed/cf-forsiking/era5/s2s-model-format/forecast/daily/values/tp24'
dir3 = '/nird/projects/NS9873K/etdu/processed/cf-forsiking/era5/s2s-model-format/hindcast/daily/values/tp24'

tpSet = wd.Weatherset(pathListToData=[dir1,dir2,dir3], onlyDirectory=True)

endDir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/maps/max/'



###   Map with full resolution and time

title = "Maximum simulated precipitations"

wd.map_of_max(data=tpSet, name='max_all-res_all-time', title=title, dir=endDir)


""" tpSet.compute_time_max(name='max_all-res_all-time')
maxToPlot = tpSet.compute['max_all-res_all-time']

boundaries = wd.boundaries(tpSet)[0]
fig, ax = geo.map(boundaries)
fig, ax = wd.showcase_data(maxToPlot, boundaries, fig, ax)

fig.suptitle(title)
fig.savefig(endDir + 'tp24-max_all-resolution_all-time.png')
geo.plt.close() """
