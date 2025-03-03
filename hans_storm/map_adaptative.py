

import sys
import getopt

sys.path.append('/home/esauvat/Documents/NORCE - Extrem weather forecasting/unseen-storm-forecasts/python_mapping_tools')
sys.path.append('/nird/projects/NSS9873K/emile/unseen-storm-forecasts/python_mapping_tools')

import maps as mp
import weatherdata as wd

###     The passed arguments are the following : 
###     --file   (can be multiple inputs separated by a comma)
###     --title
###     --day-begin
###     --day-end
###     --day-list
###     --year
###     --type    (must be one of "time_avg" or "time_sum")
###     --time-span (mandatory went not using --result)
###     --size      (size of the map)
###     --output

try: 
    opts, args = getopt.getopt(sys.argv[2:], "f:t:b:e:l:y:T:ts:s:cr:d:", 
                               [
                                   "file=", 
                                   "title=",
                                   "day-begin=",
                                   "day-end=",
                                   "day-list=",
                                   "year=",
                                   "type=",
                                   "time-span=",
                                   "size=",
                                   "coords-range=",
                                   "dir="
                                ]
                                ) 
except getopt.GetoptError as err: 
    print(f"Error: {err}") 
    sys.exit(1)


pathToFileList = []
title=None
dayBegin = None
dayEnd = None
dayList = None
type = "daily"
timeSpan = 0
size = 'medium'
coordsRange = 'largeNo'
year = "2023"
dir=None

typeDict = {
    "daily":0,
    "time_avg":1,
    "time_sum":2
}


for opt, arg in opts:
    if opt in ['-f', '--file']:
        paths = arg.split(',')
        for path in paths :
            pathToFileList.append(path)
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
    elif opt in ['-T', '--type'] :
        assert(arg in typeDict.keys())
        ("The type argument must be of " + str(typeDict.keys()))
        type = arg
    elif opt in ['-ts', '--time-span'] :
        timeSpan = int(arg)
    elif opt in ['-s', '--size'] :
        assert(arg in mp.sizes.keys())
        ("The size argument must be in " + str(mp.sizes.keys()))
        size = arg
    elif opt in ['-cr', '--coords-range'] :
        assert(arg in wd.bound_values.keys())
        ("The coordinate range argument must be in " + str(wd.bound_values.keys()))
        coordsRange = arg
    elif opt in ['-d', '--dir'] :
        dir = arg


# Some test to assert the relevance of the arguments

assert((dayBegin==None) == (dayEnd==None))
("Missing begin or end day value")

assert(((dayList==None) != (dayBegin==None)) & ((dayList==None) != (dayEnd==None)))
("Use either a day list or a begin-end day couple")

assert(len(pathToFileList)>0)
("Missing file argument")

assert((type!="daily") == (timeSpan>0))
("Missing time span argument")

assert(dir!=None)
("Missing directory argument")

if not dir.endswith('/'):
    dir += "/"


###   Program

if dayBegin :
    days = wd.np.arange(dayBegin, dayEnd)
else :
    days = wd.np.array([int(num) for num in dayList])

nbRow, nbColumn = wd.mosaic_split(len(days))

totalPrecipitation = None

def daily_data():
    return totalPrecipitation

def time_avg_data():
    return wd.mean_over_time(totalPrecipitation, span=timeSpan)

def time_sum_data():
    return wd.sum_over_time(totalPrecipitation, span=timeSpan)

def get_data():
    global type
    if type=="daily":
        return daily_data()
    elif type=="time_avg":
        return time_avg_data()
    elif type=="time_sum":
        return time_sum_data()
    print(type)
    sys.exit()
    

def draw(pathToFile:str) :

    global totalPrecipitation

    ncData = wd.Dataset(pathToFile, 'r')
    totalPrecipitation = wd.dataset_to_xr(ncData)

    boundaries, cLat, cLon = wd.boundaries(ncData, coordsRange)
    projection = mp.ccrs.LambertConformal(central_latitude=cLat, central_longitude=cLon)

    fig, axis = mp.map(nbRow, nbColumn, size, boundaries, projection)

    fullData = get_data()

    fig, axis = wd.showcase_data(fullData, boundaries, days, fig, axis)
    i=0
    for ax in axis:
        ax.set_title(wd.nbToDate(days[i], year))
        i+=1
    if title:
        fig.suptitle(title)

    pathScatter = pathToFile.split('/')
    fileName = pathScatter[-1][:-3]
    typeName = "_" + type
    if timeSpan:
        typeName += "_" + str(timeSpan)

    fig.savefig(dir + fileName.split('_')[0] + '_' + wd.nbToSortingDate(days[0], year) + typeName + ".png")

    

###   Execution

def create_map():
    for pathToFile in pathToFileList:
        draw(pathToFile)


if __name__=='__main__':
    func_name = sys.argv[1]
    globals()[func_name]()
