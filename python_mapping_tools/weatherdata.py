
''' Function to use the dataset properly '''

import maps as m

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
    
    assert(size in bound_values.keys())
    ("The size variable must be one of 'centerNo', 'largeNo' and 'fullScand'")
    
    

    s, n, w, e = bound_values[size]

    latS = max(s, data['tp24'].GRIB_latitudeOfLastGridPointInDegrees)
    latN = min(n, data['tp24'].GRIB_latitudeOfFirstGridPointInDegrees)
    lonW = max(w, data['tp24'].GRIB_longitudeOfFirstGridPointInDegrees)
    lonE = min(e, data['tp24'].GRIB_longitudeOfLastGridPointInDegrees)

    return np.array([lonW, lonE, latS, latN]), (latS + latN) / 2, (lonW + lonE) / 2


###   Showcasing the data   ###

def showcase_data(data:xr.DataArray, 
                  effectSample:xr.DataArray, 
                  indexValues, 
                  fig:m.plt.Figure, axgr:m.AxesGrid) -> tuple :

    i = 0
    vmin, vmax = effectSample.min(), effectSample.max()
    _, Y, X = data.dims

    for ax in axgr:
        p = ax.pcolormesh(data[X], data[Y], data.loc[indexValues[i]],
                          vmin=vmin,
                          vmax=vmax,
                          transform=m.projPlane)
        i += 1

    axgr.cbar_axes[0].colorbar(p)

    return fig, axgr



###   Dataset to Xarray   ###

def dataset_to_xr(data:Dataset) :
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
        data[timesIndex, :, :],
        dims=data.dims,
        coords={
            "time":data['time'][timesIndex],
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
        begin, end = t-span//2, t+(span+1)//2
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
        begin, end = t-span//2, t+(span+1)//2
        res[t,:,:]=data[max(0,begin):min(totalTime,end), :, :].mean(dim="time")
    return res


###   Day number to date   ###

def nbToDate(nb : int, year : str) -> str :
    dayNum = str(nb)
    dayNum.rjust(3 + len(dayNum), '0')
    res = datetime.strptime(year + "-" + dayNum, "%Y-%j").strftime("%m-%d-%Y")
    return res
