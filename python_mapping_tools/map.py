

import sys
import getopt
import os

""" sys.path.append('/home/esauvat/Documents/NORCE - Extrem weather forecasting/unseen-storm-forecasts/python_mapping_tools')
sys.path.append('/nird/projects/NSS9873K/emile/unseen-storm-forecasts/python_mapping_tools') """

import maps as mp
import weatherdata as wd

###     The passed arguments are the following : 
###     --file   (can be multiple inputs separated by a comma)
###     --title
###     --day-begin
###     --day-end
###     --day-list
###     --year
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
                                   "year=",
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


pathToData = None
resolution = ('0.25', '0.5')
title=None
dayBegin = None
dayEnd = None
dayList = None
hindcastYear = None
type = "daily"
timeSpan = 0
size = 'medium'
coordsRange = 'largeNo'
year = "2023"
dir=None

typeDict = {
    "daily":['',''],
    "time_avg":[' - Mean on ',' days'],
    "time_sum":[' - Sum on ', ' days']
}


for opt, arg in opts:
    if opt in ['-f', '--file']:
        pathToData = arg
    elif opt in ['-r', '--resolution']:
        resolution = (arg, arg)
    elif opt in ['-t', '--title']:
        title = arg
    elif opt in ['-b', '--day-begin'] :
        dayBegin = int(arg)
    elif opt in ['-e', '--day-end'] :
        dayEnd = int(arg)
    elif opt in ['-l', '--day-list'] :
        dayList = arg.split()
    elif opt in ['-y', '--year'] :
        year = arg
    elif opt in ['-h', '--hindcast']:
        hindcastYear = arg
    elif opt in ['-T', '--type'] :
        assert  (arg in typeDict.keys()), ("The type argument must be in " + str(typeDict.keys()))
        type = arg
    elif opt in ['-w', '--time-span'] :
        timeSpan = int(arg)
    elif opt in ['-s', '--size'] :
        assert (arg in mp.sizes.keys()), ("The size argument must be in " + str(mp.sizes.keys()))
        size = arg
    elif opt in ['g', '--geo-area'] :
        assert (arg in wd.bound_values.keys()), ("The coordinate range argument must be in " + str(wd.bound_values.keys()))
        coordsRange = arg
    elif opt in ['-d', '--dir'] :
        dir = arg


assert (pathToData), ("Missing file argument")
pathToFileList = []
if pathToData.endswith('.txt'):
    paths = open(pathToData, 'r')
    pathToFileList = paths.read().split('\n')
    if len(pathToFileList[-1])==0:
        pathToFileList.pop()
elif pathToData.endswith('/'):
    for filename in os.listdir(pathToData):
        if resolution[0] in filename or resolution[1] in filename:
            pathToFileList.append(os.path.join(pathToData, filename))
else:
    pathToFileList = pathToData.split(',')


# Some test to assert  the relevance of the arguments

assert ((dayBegin==None) == (dayEnd==None)), ("Missing begin or end day value")

assert (((dayList==None) != (dayBegin==None)) & ((dayList==None) != (dayEnd==None))), ("Use either a day list or a begin-end day couple")

assert ((type!="daily") == (timeSpan>0)), ("Missing time span argument")

assert (dir!=None), ("Missing directory argument")

if not dir.endswith('/'):
    dir += "/"


###   Program

days = []
if dayBegin :
    days = wd.np.arange(dayBegin, dayEnd+1)
else :
    days = wd.np.array([int(num) for num in dayList])

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
    if not dataDate.startswith(year):
        print(pathToFile)
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
    effectDays = range(firstDay, lastDay+1)

    n = len(effectDays)
    for i in range(n):
        if totalPrecipitation[effectDays[n-1-i],:,:].all():
            del effectDays[n-1-i]
    if effectDays==[]:
        return
    effectDays = wd.np.array(effectDays)

    nbMap = len(effectDays)
    nbRow, nbColumn = wd.mosaic_split(len(effectDays))

    boundaries, cLat, cLon = wd.boundaries(ncData, coordsRange)
    projection = mp.ccrs.LambertConformal(central_latitude=cLat, central_longitude=cLon)

    fig, axis = mp.map(nbRow, nbColumn, nbMap, size, boundaries, projection)

    fig, axis = wd.showcase_data(totalPrecipitation, boundaries, effectDays, nbMap, fig, axis)
    for i in range(nbMap):
        axis[i].set_title(wd.nbToDate(effectDays[i]+startingDate, year))
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

    mp.plt.close()

    

###   Execution

def create():
    for pathToFile in pathToFileList:
        draw(pathToFile)


if __name__=='__main__':
    func_name = sys.argv[1]
    globals()[func_name]()
