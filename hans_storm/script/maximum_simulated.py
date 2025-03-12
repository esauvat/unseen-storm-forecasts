
''' Script to make the maps of maximum total precipitations ever modeled '''

import sys

sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/python_mapping')

import weatherdata as wd
import pickle

with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/continuous_all-res.pkl', 'w') as inp:
    tpSet = pickle.load(inp)




endDir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/maps/max/'



###   Map with full resolution and time

title = "Maximum simulated precipitations"

wd.map_of_max(data=tpSet, name='max_all-res_all-time', title=title, dir=endDir)



###   Map with full resolution and annual maximum

title = "Annual maximum simulated precipitations : 2019 - 2024"
years = ['2019','2020','2021','2022','2023','2024']

wd.map_of_max(data=tpSet, name='max_all-res_2019-2024', title=title, years=years, dir=endDir)


title = "Annual maximum simulated precipitations : 2013 - 2018"
years = ['2013','2014','2015','2016','2017','2018']

wd.map_of_max(data=tpSet, name='max_all-res_2013-2018', title=title, years=years, dir=endDir)


title = "Annual maximum simulated precipitations : 2007 - 2012"
years = ['2007','2008','2009','2010','2011','2012']

wd.map_of_max(data=tpSet, name='max_all-res_2007-2012', title=title, years=years, dir=endDir)



###   Map with full resolution and decadal maximum

title = "Decadal maximum simulated precipitations : 1941 - 2024"
years = ['1940','1950','1960','1970','1980','1990','2000','2010','2020']
timeSpan = 10
sizeMap = 'large'

wd.map_of_max(data=tpSet, name = 'max_all-res_2007-2012-dec', title=title, years=years, timeSpan=timeSpan, sizeMap=sizeMap, dir=endDir)
