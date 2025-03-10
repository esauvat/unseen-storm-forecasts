
import sys
import getopt
import os

""" sys.path.append('/home/esauvat/Documents/NORCE - Extrem weather forecasting/unseen-storm-forecasts/python_mapping_tools')
sys.path.append('/nird/projects/NSS9873K/emile/unseen-storm-forecasts/python_mapping_tools') """

import geographics as geo
import weatherdata as wd

###     The passed arguments are the following : 
###     --file   (can be multiple inputs separated by a comma)
###     --resolution
###     --title
###     --day-begin
###     --day-end
###     --day-list
###     --years
###     --hindcast date
###     --type    (must be one of "time_avg" or "time_sum")
###     --time-span (mandatory went not using --result)
###     --size      (size of the map)
###     --coordinates
###     --directory

try: 
    opts, args = getopt.getopt(sys.argv[2:], "f:r:t:b:e:l:y:h:T:w:s:g:d:", 
                               [
                                   "file=",
                                   "resolution=",
                                   "title=",
                                   "day-begin=",
                                   "day-end=",
                                   "day-list=",
                                   "years=",
                                   "hindcast=",
                                   "type=",
                                   "time-span=",
                                   "size=",
                                   "geo-area=",
                                   "dir="
                                ]
                                ) 
except getopt.GetoptError as err: 
    print(f"Error: {err}") 
    sys.exit(1)


pathListToData = []
resolution = None
title=None
dayBegin = None
dayEnd = None
dayList = None
hindcastYear = None
type = None
timeSpan = 0
size = 'medium'
coordsRange = 'largeNo'
years = []
dir=None

typeDict = {
    "daily":['',''],
    "time_avg":[' - Mean on ',' days'],
    "time_sum":[' - Sum on ', ' days'],
    "max_map":[]
}


for opt, arg in opts:
    if opt in ['-f', '--file']:
        pathListToData = arg
    elif opt in ['-r', '--resolution']:
        resolution = arg
    elif opt in ['-t', '--title']:
        title = arg
    elif opt in ['-b', '--day-begin'] :
        dayBegin = int(arg)
    elif opt in ['-e', '--day-end'] :
        dayEnd = int(arg)
    elif opt in ['-l', '--day-list'] :
        dayList = arg.split()
    elif opt in ['-y', '--years'] :
        years = arg.split(',')
    elif opt in ['-h', '--hindcast']:
        hindcastYear = arg
    elif opt in ['-T', '--type'] :
        assert  (arg in typeDict.keys()), ("The type argument must be in " + str(typeDict.keys()))
        type = arg
    elif opt in ['-w', '--time-span'] :
        timeSpan = int(arg)
    elif opt in ['-s', '--size'] :
        assert (arg in geo.sizes.keys()), ("The size argument must be in " + str(geo.sizes.keys()))
        size = arg
    elif opt in ['g', '--geo-area'] :
        assert (arg in wd.bound_values.keys()), ("The coordinate range argument must be in " + str(wd.bound_values.keys()))
        coordsRange = arg
    elif opt in ['-d', '--dir'] :
        dir = arg


# Some test to assert  the relevance of the arguments

assert (pathListToData!=[]), ("Missing file argument")

if type in ["daily","time_avg","time_sum"]:
    assert ((dayBegin==None) == (dayEnd==None)), ("Missing begin or end day value")
    assert (((dayList==None) != (dayBegin==None)) & ((dayList==None) != (dayEnd==None))), ("Use either a day list or a begin-end day couple")

if type in ["time_avg","time_sum"]:
    assert timeSpan>0, ("Missing time span argument")

assert (dir!=None), ("Missing directory argument")

if not dir.endswith('/'):
    dir += "/"


###   Program

""" days = []
if dayBegin :
    days = wd.np.arange(dayBegin, dayEnd+1)
else :
    days = wd.np.array([int(num) for num in dayList]) """
# This has been moved in the draw function in an other branch

totalPrecipitation = None
    

def get_data():
    global totalPrecipitation
    if type=="time_avg":
        totalPrecipitation = wd.mean_over_time(totalPrecipitation, span=timeSpan)
    elif type=="time_sum":
        totalPrecipitation = wd.sum_over_time(totalPrecipitation, span=timeSpan)
    elif type=="space_avg":
        totalPrecipitation = wd.mean_over_space(totalPrecipitation, span=timeSpan)
    elif type=="space_sum":
        totalPrecipitation = wd.sum_over_space(totalPrecipitation, span=timeSpan)


def draw(pathToFile:str) :

    dataDate = pathToFile.split('_')[-1]
    if len(years)!=0 and not any(dataDate.startswith(y) for y in years):
        return

    global totalPrecipitation

    ncData = wd.Dataset(pathToFile, 'r')

    startingDate = 0

    if 'hindcast' in pathToFile:
        fileDate = pathToFile[-8:-3].split('-')
        hindcastDate = int(
            hindcastYear + fileDate[0] + fileDate[1]
        )
        startingDate = wd.getDayNumber(pathToFile[-13:-3])
    else:
        hindcastDate = None

    totalPrecipitation = wd.dataset_to_xr(ncData, hindcastDate)

    get_data()

    firstDay, lastDay = days[0]-startingDate, days[-1]-startingDate
    firstData, lastData = ncData['time'][0], ncData['time'][-1]
    if lastDay<firstData or firstDay>lastData :
        return
    else :
        firstDay = max(firstDay, firstData)
        lastDay = min(lastDay, lastData)
    effectDays = list(wd.np.arange(firstDay, lastDay+1))

    n = len(effectDays)
    for i in range(n):
        if not totalPrecipitation.sel(time=effectDays[n-1-i]).all():
            del effectDays[n-1-i]
    if effectDays==[]:
        return
    effectDays = wd.np.array(effectDays)

    nbMap = len(effectDays)
    nbRow, nbColumn = wd.mosaic_split(len(effectDays))

    boundaries, cLat, cLon = wd.boundaries(ncData, coordsRange)
    projection = geo.ccrs.LambertConformal(central_latitude=cLat, central_longitude=cLon)

    fig, axis = geo.map(nbRow, nbColumn, nbMap, size, boundaries, projection)

    fig, axis = wd.showcase_data(totalPrecipitation, boundaries, nbMap, fig, axis, timesIndex=effectDays)
    for i in range(nbMap):
        axis[i].set_title(wd.nbToDate(effectDays[i]+startingDate, year))                            #### TODO : need to be updated to conform to the multi years selection possibility
    if title:
        if type=='daily':
            fig.suptitle(title)
        else:
            fig.suptitle(title+typeDict[type][0]+str(timeSpan)+typeDict[type][1])

    pathScatter = pathToFile.split('/')
    dataType = 'test'
    if 'continuous-format' in pathScatter:
        dataType = 'continuous'
    elif 'forecast' in pathScatter:
        dataType = 'forecast'
    elif 'hindcast' in pathScatter:
        dataType = 'hindcast_'+ hindcastYear
    fileName = pathScatter[-1][4:-3]
    typeName = "_" + type
    if timeSpan:
        typeName += "_" + str(timeSpan)

    fig.savefig(dir + dataType + fileName + typeName + ".png")

    geo.plt.close()



def map_of_max():

    dataset = wd.Weatherset(pathListToData, resolution=resolution, years=years)

    nbRows, nbColumns, nbMaps =  1, 1, 1
    
    if len(years)!=0:
        dataarrays = []
        for y in years:
            if timeSpan:
                yearsSample = [str(i) for i in range(int(y), int(y)+timeSpan)]
                data_max = dataset.max('time', time_sel=yearsSample)
            else:
                data_max = dataset.max('time', time_sel=y)
            data_max = data_max.to_dataarray()
            data_max = data_max.rename({"variable":"time"}).reindex(time=[y])
            dataarrays.append(data_max.transpose("time", "latitude", "longitude"))
        max_simulated = wd.xr.concat(dataarrays, dim="time")
        nbMaps = len(years)
        nbRows, nbColumns = wd.mosaic_split(nbMaps)
    else:
        max_simulated = dataset.max('time').to_dataarray()
        max_simulated = max_simulated.rename({"variable":"time"}).reindex(time=[0])

    boundaries = wd.boundaries(dataset, size=coordsRange)

    fig, axis = geo.map(n=nbRows, p=nbColumns, nbMap=nbMaps, size=size, boundaries=boundaries)

    fig, axis = wd.showcase_data(max_simulated, boundaries, nbMaps, fig, axis)

    if len(years)!=0:
        for i in range(nbMaps):
            axis[i].set_title(years[i])
    elif title:
        fig.suptitle(title)

    timeReference, resReference = '_all-time', '_all-resolution'
    if len(years)!=0: 
        timeReference = '_' + years[0] + '-' + years[-1]
    if resolution:
        resReference = '_' + resolution + 'x' + resolution

    fig.savefig(dir+'tp24-max_' + resReference + timeReference + '.png')

    geo.plt.close()

    

###   Execution

def create():

    pathToFileList = []

    for loc in pathListToData:
        if loc.endswith('/'):
            for filename in os.listdir(loc):
                if not resolution or resolution in filename:
                    pathToFileList.append(os.path.join(loc, filename))
        elif loc.endswith('.txt'):
            paths = open(loc, 'r').read().split('\n')
            if paths[-1]=='':
                pathToFileList.pop()
            for path in paths:
                pathToFileList.append(path)
        else:
            for path in loc.split(','):
                pathToFileList.append(path)

    for pathToFile in pathToFileList:
        draw(pathToFile)


if __name__=='__main__':
    func_name = sys.argv[1]
    globals()[func_name]()