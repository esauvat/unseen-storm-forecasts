
''' Function to use the dataset properly '''

import geographics as geo

import numpy as np
import pandas as pd
import xarray as xr
from netCDF4 import Dataset
from datetime import datetime, date, timedelta
import os

bound_values = {
    'centerNo':(59.7, 62.1, 6.6, 11.5),
    'largeNo':(57, 66, 3, 17),
    'fullScand':(55, 71.4 , 1.5, 32.4)
}

alphaMonths = {
    1:'January', 2:'February', 3:'March', 4:'April', 
    5:'May', 6:'June', 7:'July', 8:'August', 
    9:'September', 10:'October', 11:'November', 12:'December' 
}

###   Defining map size   ###

def boundaries(data:Dataset, size:str = 'largeNo') -> tuple :
    ''' Correcting, if needed, a wanted value for the coordinates range
    to make sure it fits the data '''
    
    assert (size in bound_values.keys()), "The size variable must be one of 'centerNo', 'largeNo' and 'fullScand'"

    s, n, w, e = bound_values[size]                                                         # Accessing the wanted values for the boundaries

    latS = max(s, data.coords['latitude'][-1])                                              # Correcting each value if necessary to make sure the map 
    latN = min(n, data.coords['latitude'][0])                                               # does not outrange the data 
    lonW = max(w, data.coords['longitude'][0])
    lonE = min(e, data.coords['longitude'][-1])

    return np.array([lonW, lonE, latS, latN]), (latS + latN) / 2, (lonW + lonE) / 2


###   Showcasing the data   ###

def showcase_data(data:xr.DataArray, 
                  boundaries:np.ndarray, 
                  fig:geo.plt.Figure, axgr:geo.AxesGrid,
                  nbMap:int=1,
                  **kwargs:np.ndarray) -> tuple :
    
    extent = kwargs.get('extent', None)

    if not 'time' in data.dims:
        data = data.expand_dims("time").transpose("time","latitude","longitude")            # If no time dimension, reshape the array to fit the data access later
        
    timesIndex = kwargs.get('timesIndex', data['time'])                                     # Setting the default value for the time selection to all the dataset
    assert((timesIndex.min()>=data['time'][0]) & (timesIndex.max()<=data['time'][-1]))      # Checking if the time selection does not get out of range for the dataset's dimension
    
    if extent:
        vmin, vmax = extent
    else:
        effectSample = select_sample(data, boundaries, timesIndex)                          # Selecting the values of the dataset that will be plotted to determine the best extent for the colorbar
        vmin, vmax = effectSample.min(skipna=True), effectSample.max(skipna=True)           # Computing the range of the colorbar
    
    _, Y, X = data.dims
    for i in range(nbMap):
        p = axgr[i].pcolormesh(data[X], data[Y], data.loc[timesIndex[i]],                   # Plotting each set of value on the corresponding subplot
                          vmin=vmin,
                          vmax=vmax,
                          transform=geo.projPlane)

    axgr.cbar_axes[0].colorbar(p)                                                           # Adding the colorbar

    return fig, axgr



""" # Outdated

###   Dataset to Xarray   ###

def dataset_to_xr(data:Dataset, hindcastDate) :
    if hindcastDate :
        tab = xr.DataArray(
            data['tp24'][:,:,:,:],
            dims=("hdate", "time", "latitude", "longitude"),
            coords={
                "hdate":data['hdate'][:],
                "time":data['time'][:],
                "latitude":data['latitude'][:],
                "longitude":data['longitude'][:]
            }
        )
        res = xr.DataArray(
            tab.sel(hdate=hindcastDate).values,
            dims=tab.dims[1:],
            coords={key:tab.coords[key] for key in tab.dims[1:]}
        )
        return res
    res = xr.DataArray(
        data['tp24'][:,:,:], 
        dims=("time", "latitude", "longitude"), 
        coords={
            "time":data['time'][:],
            "latitude":data['latitude'][:], 
            "longitude":data['longitude'][:]
        }
    )
    return res """


###   Select echantillon   ###

def select_area(data:xr.DataArray, boundaries:np.ndarray) :
    ''' Select the data in the geographic range that will be plotted '''

    [lonW, lonE, latS, latN] = boundaries

    iLonW = np.where(np.isclose(data['longitude'], lonW))[0][0]                             # Getting the index for each of the extreme 
    iLonE = np.where(np.isclose(data['longitude'], lonE))[0][0]                             # values of the latitude and longitude
    iLatS = np.where(np.isclose(data['latitude'], latS))[0][0]
    iLatN = np.where(np.isclose(data['latitude'], latN))[0][0]

    ''' # Remark
    The following part can probably be inproved using xr.DataArray.copy() '''

    res = xr.DataArray(
        data[:, iLatN:iLatS+1, iLonW:iLonE+1],                                              # Selecting the wanted data
        dims=data.dims,
        coords={
            "time":data['time'],
            "latitude":data['latitude'][iLatN:iLatS+1],                                     # Adjusting latitude coordinate
            "longitude":data['longitude'][iLonW:iLonE+1]                                    # Adjusting longitude coordinate
        }
    )
    return res

def select_time(data:xr.DataArray, timesIndex:np.ndarray) -> xr.DataArray :
    ''' Select the data in the time range that will be plotted '''

    ''' # Remark
    As above, probable improvment '''

    res = xr.DataArray(
        data.loc[timesIndex, :, :],                                                         # Selecting the wanted data
        dims=data.dims,
        coords={
            "time":timesIndex,                                                              # Adjusting time coordinate
            "latitude":data['latitude'],
            "longitude":data['longitude']
        }
    )
    return res

def select_sample(data:xr.DataArray, boundaries:np.ndarray, timesIndex:np.ndarray) -> xr.DataArray :
    res = select_area(data, boundaries)
    res = select_time(res, timesIndex)
    return res



###   Xarray Operations   ###

def sum_over_time(data:xr.DataArray, span:int) -> xr.DataArray :
    res = xr.full_like(data, 0)                                                             # Creating an empty copy
    totalTime = len(data['time'])
    for t in range(totalTime):
        begin, end = t-span//2, t+(span+1)//2                                               # Setting the time range for the sum
        if begin>=0 & end <= totalTime :                                                    # Checking if all the time to sum exist
            res[t,:,:]=data[begin:end, :, :].sum(dim="time")
        else :
            res[t,:,:]=None
    return res

def mean_over_time(data:xr.DataArray, span:int) -> xr.DataArray :
    res = xr.full_like(data, 0)                                                             # Creating an empty copy
    totalTime = len(data['time'])
    for t in range(totalTime):
        begin, end = t-span//2, t+(span+1)//2                                               # Setting the time range for the mean
        res[t,:,:]=data[max(0,begin):min(totalTime,end), :, :].mean(dim="time")
    return res

def sum_over_space(data:xr.DataArray, span:int) -> xr.DataArray :
    res = xr.full_like(data, 0)                                                             # Creating an empty copy
    nbLat = len(data['latitude'])
    nbLon = len(data['longitude'])
    for y in range(nbLat):
        yBegin, yEnd = y-span//2, y+(span+1)//2                                             # Creating the latitude range for the sum
        if yBegin>=0 & yEnd<=nbLat:                                                         # Checking if all the latitude indexes to sum exist
            for x in range(nbLon):
                xBegin, xEnd = x-span//2, x+(span+1)//2                                     # Creating the longitude range for the sum
                if xBegin>=0 & xEnd<=nbLon:                                                 # Checking if all the longitude indexes to sum exist
                    res[:,y,x] = data[:, yBegin:yEnd, xBegin:xEnd].sum(
                        dim=["latitude","longitude"]
                    )
                else:
                    res[:,y,x] = None
        else:
            res[:,y,:] = np.zeros_like(data['tp24'][:,y,:]).fill(None)
    return res

def mean_over_space(data:xr.DataArray, span:int) -> xr.DataArray :
    res = xr.full_like(data, 0)                                                             # Creating an empty copy
    nbLat = len(data['latitude'])
    nbLon = len(data['longitude'])    
    for y in range(nbLat):
        yBegin, yEnd = y-span//2, y+(span+1)//2                                             # Creating the latitude range for the mean
        for x in range(nbLon):
            xBegin, xEnd = x-span//2, x+(span+1)//2                                         # Creating the longitude range for the mean
            res[:,y,x]=data[:, yBegin:yEnd, xBegin:xEnd].mean(
                dim=["latitude", "longitude"]
            )
    return res

###   Day number to date   ###

def nbToDate(nb : int, year : str) -> str :
    dayNum = str(nb)
    dayNum.rjust(3 + len(dayNum), '0')
    res = datetime.strptime(year + "-" + dayNum, "%Y-%j").strftime("%d-%m-%Y")
    return res

def nbToSortingDate(nb : int, year : str) -> str :
    dayNum = str(nb)
    dayNum.rjust(3 + len(dayNum), '0')
    res = datetime.strptime(year + "-" + dayNum, "%Y-%j").strftime("%Y-%m-%d")
    return res

def getDayNumber(date):
    dayNum = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%j")
    res = dayNum.split('-')[1]
    return int(res)


###   Mosaic Split : give the best mosaic for a given day list

def mosaic_split(nbMaps:int) -> tuple[int,int] :
    nbRow = 1
    while True :
        ''' The loop ends because nbRow grows strictly and 
        for nbRow==nbMaps the condition is valid'''
        nbColumn = nbMaps//nbRow + (nbMaps%nbRow > 0)
        if nbColumn-nbRow <= 1:
            return nbRow, nbColumn
        nbRow += 1



###   Handle Directories

def extract_files(dir:str, pathsToFiles:list):
    type = ''
    pathScatter = dir.split('/')
    while pathScatter!=[]:
        subDir = pathScatter.pop()
        if subDir == 'daily':
            type = pathScatter[-1].split('-')[0]
            break
    assert type!='' , "Wrong directory"
    for filename in os.listdir(dir):
        pathsToFiles[(type, filename[:-3])] = os.path.join(dir, filename)


###   Reindexing hindcasts

def reindex_hindcast(da:xr.DataArray):
    ''' Reindexing the ('hdate','time') dimension for hincast files '''
    da = da.stack(fullTime=["hdate","time"])                                                # Combining the 2 time related coordinates
    newIndexes = []
    for (hdate,time) in da['fullTime'].values:                                              # Creating the new indexes
        hyear = hdate // 10000
        isLeapYearCase = (time.day==29) and (time.month==2) and ((time.year-hyear)%4!=0)    # Checking if the date exists if the hindcast is started at hdate
        if isLeapYearCase:
            newIndexes.append(time.replace(day=1,month=3,year=hyear))
        else:
            newIndexes.append(time.replace(year=hyear))
    reindexed_da = xr.DataArray(
        da.values,
        dims=("latitude","longitude","time"),
        coords={
            "latitude":da['latitude'],
            "longitude":da['longitude'],
            "time":np.array(newIndexes)
        }
    )
    return reindexed_da
