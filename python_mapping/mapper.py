
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
        pathListToData = arg.split(',')
    elif opt in ['-r', '--resolution']:
        resolution = arg
    elif opt in ['-t', '--title']:
        title = arg
    elif opt in ['-b', '--day-begin'] :
        dayBegin = arg
    elif opt in ['-e', '--day-end'] :
        dayEnd = arg
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
    assert dayBegin, ("Missing begin or end day value")
    if not dayEnd:
        dayEnd=dayBegin
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

    totalPrecipitation = wd.xr.open_dataarray(pathToFile).drop_vars("number", errors="ignore")

    get_data()

    if dayBegin: 
        days = wd.np.arange(wd.np.datetime64(dayBegin), wd.np.datetime64(dayEnd)+wd.np.timedelta64(1,'D'))
    else:
        days = wd.np.array([wd.np.datetime64(day) for day in dayList])

    firstDay, lastDay = days[0], days[-1]
    firstData, lastData = totalPrecipitation['time'][0], totalPrecipitation['time'][-1]
    if lastDay<firstData or firstDay>lastData :
        return
    else :
        firstDay = max(firstDay, firstData)
        lastDay = min(lastDay, lastData)
    effectDays = list(wd.np.arange(firstDay, lastDay+wd.np.timedelta64(1, 'D')))

    n = len(effectDays)
    for i in range(n):
        if wd.np.any(totalPrecipitation.sel(time=effectDays[n-1-i]).values == None):
            del effectDays[n-1-i]
    if effectDays==[]:
        return
    effectDays = wd.np.array(effectDays)
    
    nbMap = len(effectDays)
    nbRow, nbColumn = wd.mosaic_split(len(effectDays))

    boundaries, cLat, cLon = wd.boundaries(data=totalPrecipitation, size=coordsRange)
    projection = geo.ccrs.LambertConformal(central_latitude=cLat, central_longitude=cLon)

    fig, axis = geo.map(nbRow, nbColumn, nbMap, size, boundaries, projection)

    fig, axis = wd.showcase_data(totalPrecipitation, boundaries, fig, axis, nbMap, timesIndex=effectDays)
    for i in range(nbMap):
        axis[i].set_title(wd.np.datetime_as_string(effectDays[i]))
    if title:
        if type=='daily':
            fig.suptitle(title)
        else:
            fig.suptitle(title+typeDict[type][0]+str(timeSpan)+typeDict[type][1])

    pathScatter = pathToFile.split('/')
    dataType = 'test'
    if'continuous-format' in pathScatter:
        dataType = 'continuous'
    elif 'forecast' in pathScatter:
        dataType = 'forecast'
    elif 'hindcast' in pathScatter:
        dataType = 'hindcast_'+ hindcastYear
    if resolution:
        resRef = '_' + resolution + 'x' + resolution
    else:
        resRef = '_all-res'
    typeName = "_" + type
    if timeSpan:
        typeName += "_" + str(timeSpan)
    date = '_' + str(firstDay)
    if lastDay != firstDay:
        date += '-' + str(lastDay)

    fig.savefig(dir + dataType + resRef + date + typeName + ".png")

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