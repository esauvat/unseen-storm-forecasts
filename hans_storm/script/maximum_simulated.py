
''' Script to make the maps of maximum total precipitations ever modeled '''

import sys

sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/python_mapping')

import weatherdata as wd
import pickle

with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/continuous_all-res.pkl', 'rb') as inp:
    tpSet = pickle.load(inp)


endDir = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/maps/max/'


def all_res_all_time():
    """ Map with full resolution and time """

    name = 'continuous_max_all-res_all-time'
    title = "Maximum simulated precipitations"

    if name in tpSet.compute.keys():
        with open(tpSet.compute[name], 'rb') as inp:
            data = pickle.load(inp)
            fig, _ = wd.draw_map(data, title=title)
            fig.savefig(endDir+'tp24_all-res_all-time.png')
    else:
        res = wd.map_of_max(data=tpSet, title=title, dir=endDir, splitYears=True)
        path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/results/' + name + '.pkl'
        with open(path, 'wb') as outp:
            pickle.dump(res, outp, pickle.HIGHEST_PROTOCOL)
            tpSet.compute[name] = path



def all_res_annual():
    """ Map with full resolution and annual maximum """

        # 2019-2024
    name = 'continuous_max_all-res_2019-2024'
    title = "Annual maximum simulated precipitations : 2019 - 2024"
    years = ['2019','2020','2021','2022','2023','2024']

    if name in tpSet.compute.keys():
        with open(tpSet.compute[name], 'rb') as inp:
            data = pickle.load(inp)
            fig, _ = wd.draw_map(data, title=title, times=years)
            fig.savefig(endDir+'tp24_all-res_2019-2024.png')
    else:
        res = wd.map_of_max(data=tpSet, title=title, years=years, splitYears=True, dir=endDir)
        path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/results/' + name + '.pkl'
        with open(path, 'wb') as outp:
            pickle.dump(res, outp, pickle.HIGHEST_PROTOCOL)
            tpSet.compute[name] = path


        # 2013-2018
    name = 'continuous_max_all-res_2013-2018'
    title = "Annual maximum simulated precipitations : 2013 - 2018"
    years = ['2013','2014','2015','2016','2017','2018']

    if name in tpSet.compute.keys():
        with open(tpSet.compute[name], 'rb') as inp:
            data = pickle.load(inp)
            fig, _ = wd.draw_map(data, title=title, times=years)
            fig.savefig(endDir+'tp24_all-res_2013-2018.png')
    else:
        res = wd.map_of_max(data=tpSet, title=title, years=years, splitYears=True, dir=endDir)
        path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/results/' + name + '.pkl'
        with open(path, 'wb') as outp:
            pickle.dump(res, outp, pickle.HIGHEST_PROTOCOL)
            tpSet.compute[name] = path


        # 2007-2012
    name = 'continuous_max_all-res_2007-2012'
    title = "Annual maximum simulated precipitations : 2007 - 2012"
    years = ['2007','2008','2009','2010','2011','2012']

    if name in tpSet.compute.keys():
        with open(tpSet.compute[name], 'rb') as inp:
            data = pickle.load(inp)
            fig, _ = wd.draw_map(data, title=title, times=years)
            fig.savefig(endDir+'tp24_all-res_2007-2012.png')
    else:
        res = wd.map_of_max(data=tpSet, title=title, years=years, splitYears=True, dir=endDir)
        path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/results/' + name + '.pkl'
        with open(path, 'wb') as outp:
            pickle.dump(res, outp, pickle.HIGHEST_PROTOCOL)
            tpSet.compute[name] = path



def all_res_decadal():
    """ Map with full resolution and decadal maximum """

    name = 'continuous_max_all-res_1941-2024-dec'
    title = "Decadal maximum simulated precipitations : 1941 - 2024"
    years = ['1940','1950','1960','1970','1980','1990','2000','2010','2020']
    sizeMap = 'large'
    
    if name in tpSet.compute.keys():
        with open(tpSet.compute[name], 'rb') as inp:
            data = pickle.load(inp)
            fig, _ = wd.draw_map(data, title=title, times=years, sizeMap=sizeMap)
            fig.savefig(endDir+'tp24_all-res_1941-2024-dec.png')
    else:
        timeSpan = 10
        res = wd.map_of_max(data=tpSet, title=title, years=years, splitYears=True, timeSpan=timeSpan, sizeMap=sizeMap, dir=endDir)
        path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/results/' + name + '.pkl'
        with open(path, 'wb') as outp:
            pickle.dump(res, outp, pickle.HIGHEST_PROTOCOL)
            tpSet.compute[name] = path

def all_res_monthly():
    """ Map with full resolution and monthly maximum """

    name = 'continuous_max_all-res_monthly '
    title = "Monthly maximum recorded precipitations"
    months = [i for i in range(1,13)]

    if name in tpSet.compute.keys():
        with open(tpSet.compute[name], 'rb') as inp:
            data = pickle.load(inp)
            for month in months:
                alphaMonth = wd.alphaMonths[month]
                fig, _ = wd.draw_map(data.sel[month], title=title+' : '+alphaMonth)
                fig.savefig(endDir+'tp24_all-res_'+alphaMonth)
    else:
        res = wd.map_of_max(data=tpSet, title=title, months=months, dir=endDir)
        path = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/results/' + name + '.pkl'
        with open(path, 'wb') as outp:
            pickle.dump(res, outp, pickle.HIGHEST_PROTOCOL)
            tpSet.compute[name] = path


if __name__=='__main__':
    func_name = sys.argv[1]
    globals()[func_name]()

with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/hans_storm/data/weathersets/continuous_all-res.pkl', 'wb') as outp:
    pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)