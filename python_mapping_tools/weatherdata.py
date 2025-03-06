
''' Function to use the dataset properly '''

import maps as mp

import numpy as np
import xarray as xr
from netCDF4 import Dataset
from datetime import datetime

bound_values = {
    'centerNo':(59.7, 62.1, 6.6, 11.5),
    'largeNo':(57, 66, 3, 17),
    'fullScand':(55, 71.4 , 1.5, 32.4)
}

###   Defining map size   ###

def boundaries(data:Dataset, size:str = 'largeNo') -> tuple :
    
    assert (size in bound_values.keys()), ("The size variable must be one of 'centerNo', 'largeNo' and 'fullScand'")

    s, n, w, e = bound_values[size]

    latS = max(s, data['latitude'][-1])
    latN = min(n, data['latitude'][0])
    lonW = max(w, data['longitude'][0])
    lonE = min(e, data['longitude'][-1])

    return np.array([lonW, lonE, latS, latN]), (latS + latN) / 2, (lonW + lonE) / 2


###   Showcasing the data   ###

def showcase_data(data:xr.DataArray, 
                  boundaries:np.ndarray, 
                  timesIndex:np.ndarray, 
                  nbMap:int,
                  fig:mp.plt.Figure, axgr:mp.AxesGrid) -> tuple :

    effectSample = select_sample(data, boundaries, timesIndex)

    vmin, vmax = effectSample.min(), effectSample.max()
    _, Y, X = data.dims

    for i in range(nbMap):
        p = axgr[i].pcolormesh(data[X], data[Y], data.loc[timesIndex[i]],
                          vmin=vmin,
                          vmax=vmax,
                          transform=mp.projPlane)

    axgr.cbar_axes[0].colorbar(p)

    return fig, axgr



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
    return res


###   Select echantillon   ###

def select_area(data:xr.DataArray, boundaries:np.ndarray) :
    [lonW, lonE, latS, latN] = boundaries

    iLonW = np.where(np.isclose(data['longitude'], lonW))[0][0]
    iLonE = np.where(np.isclose(data['longitude'], lonE))[0][0]
    iLatS = np.where(np.isclose(data['latitude'], latS))[0][0]
    iLatN = np.where(np.isclose(data['latitude'], latN))[0][0]

    res = xr.DataArray(
        data[:, iLatN:iLatS+1, iLonW:iLonE+1],
        dims=data.dims,
        coords={
            "time":data['time'],
            "latitude":data['latitude'][iLatN:iLatS+1],
            "longitude":data['longitude'][iLonW:iLonE+1]
        }
    )

    return res

def select_time(data:xr.DataArray, timesIndex:np.ndarray) -> xr.DataArray :
    res = xr.DataArray(
        data.loc[timesIndex, :, :],
        dims=data.dims,
        coords={
            "time":timesIndex,
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
    res = xr.DataArray(
        np.zeros_like(data.values),
        dims=data.dims,
        coords=data.coords
    )
    totalTime = len(data['time'])
    for t in range(totalTime):
        begin, end = t-(span-1)//2, t+1+span//2
        if begin>=0 & end <= totalTime :
            res[t,:,:]=data[begin:end, :, :].sum(dim="time")
        else :
            res[t,:,:]=None
    return res

def mean_over_time(data:xr.DataArray, span:int) -> xr.DataArray :
    res = xr.DataArray(
        np.zeros_like(data.values),
        dims=data.dims,
        coords=data.coords
    )
    totalTime = len(data['time'])
    for t in range(totalTime):
        begin, end = t-(span-1)//2, t+1+span//2
        res[t,:,:]=data[max(0,begin):min(totalTime,end), :, :].mean(dim="time")
    return res

def sum_over_space(data:xr.DataArray, span:int) -> xr.DataArray :
    res = xr.DataArray(
        np.zeros_like(data.values),
        dims=data.dims,
        coords=data.coords
    )
    nbLat = len(data['latitude'])
    nbLon = len(data['longitude'])
    for y in range(nbLat):
        yBegin, yEnd = y-span//2, y+(span+1)//2
        if yBegin>=0 & yEnd<=nbLat:
            for x in range(nbLon):
                xBegin, xEnd = x-span//2, x+(span+1)//2
                if xBegin>=0 & xEnd<=nbLon:
                    res[:,y,x] = data[:, yBegin:yEnd, xBegin:xEnd].sum(dim=["latitude","longitude"])
                else:
                    res[:,y,x] = None
        else:
            res[:,y,:] = np.zeros_like(data['tp24'][:,y,:]).fill(None)
    return res

def mean_over_space(data:xr.DataArray, span:int) -> xr.DataArray :
    res = xr.DataArray(
        np.zeros_like(data.values),
        dims=data.dims,
        coords=data.coords
    )
    nbLat = len(data['latitude'])
    nbLon = len(data['longitude'])    
    for y in range(nbLat):
        yBegin, yEnd = y-span//2, y+(span+1)//2
        for x in range(nbLon):
            xBegin, xEnd = x-span//2, x+(span+1)//2
            res[:,y,x]=data[:, yBegin:yEnd, xBegin:xEnd].mean(dim=["latitude", "longitude"])
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

def mosaic_split(nbFig:int):
    nbRow = 1
    while True :
        ''' The loop ends because nbRow grows strictly and 
        for nbRow==nbFig the condition is valid'''
        nbColumn = nbFig//nbRow + (nbFig%nbRow > 0)
        if nbColumn-nbRow <= 1:
            return nbRow, nbColumn
        nbRow += 1