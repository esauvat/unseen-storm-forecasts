
''' Script to make the maps of maximum total precipitations ever modeled '''

import sys

sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/python_mapping')

import weatherdata as wd

""" dir1 = '/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/continuous-format/daily/tp24'
dir2 = '/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/s2s-model-format/forecast/daily/values/tp24'
dir3 = '/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/s2s-model-format/hindcast/daily/values/tp24'

tpSet = wd.Weatherset(pathListToData=[dir1,dir2,dir3], onlyDir=True) """

testPath = ['hans_storm/data/hindcast/daily',
            'hans_storm/data/forecast/daily',
            'hans_storm/data/continuous/daily']

tpSet = wd.Weatherset(pathListToData=testPath, onlyDir=True)

endDir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/maps/max/'



###   Map with full resolution and time

title = "Maximum simulated precipitations"

wd.map_of_max(data=tpSet, name='max_all-res_all-time', title=title, dir=endDir)
