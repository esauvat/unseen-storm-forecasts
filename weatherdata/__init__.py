""" Function to use the dataset properly """

import numpy as np
import xarray as xr
import pandas as pd
from datetime import datetime
import os
import numpy.ma as ma
import geographics as geo

bound_values = {
    'centerNo': (59.7, 62.1, 6.6, 11.5),
    'largeNo': (57, 66, 3, 17),
    'fullScand': (55, 71.4, 1.5, 32.4)
}

alphaMonths = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}


###   Defining map size   ###

def boundaries(
        data: xr.DataArray,
        size: str | None = 'largeNo',
) -> tuple:
    """ Correcting, if needed, a wanted value for the coordinates range
    to make sure it fits the data """

    assert (size in bound_values.keys()), "The size variable must be one of 'centerNo', 'largeNo' and 'fullScand'"

    s, n, w, e = bound_values[size]  # Accessing the wanted values for the boundaries

    latS = max(s, data.coords['latitude'][-1])  # Correcting each value if necessary to make sure the map
    latN = min(n, data.coords['latitude'][0])  # does not outrange the data
    lonW = max(w, data.coords['longitude'][0])
    lonE = min(e, data.coords['longitude'][-1])

    return np.array([lonW, lonE, latS, latN]), (latS + latN) / 2, (lonW + lonE) / 2


###   Showcasing the data   ###

def showcase_data(
        data: xr.DataArray,
        boundValues: np.ndarray,
        fig: geo.plt.Figure, axgr: geo.AxesGrid,
        nbMap: int | None = 1,
        **kwargs: np.ndarray
) -> tuple:
    extent = kwargs.get('extent', [])

    if 'time' not in data.dims:
        data = data.expand_dims("time").transpose("time", "latitude",
                                                  "longitude")  # If no time dimension, reshape the array to fit the data access later

    timesIndex = kwargs.get('timesIndex',
                            data['time'])  # Setting the default value for the time selection to all the dataset
    assert ((timesIndex.min() >= data['time'][0]) & (timesIndex.max() <= data['time'][
        -1]))  # Checking if the time selection does not get out of range for the dataset's dimension

    if extent:
        vmin, vmax = extent
    else:
        effectSample = select_sample(data, boundValues,
                                     timesIndex)  # Selecting the values of the dataset that will be plotted to determine the best extent for the colorbar
        vmin, vmax = effectSample.min(skipna=True), effectSample.max(skipna=True)  # Computing the range of the colorbar

    _, Y, X = data.dims
    for i in range(nbMap):
        p: object = axgr[i].pcolormesh(data[X], data[Y], data.loc[timesIndex[i]],
                                       # Plotting each set of value on the corresponding subplot
                                       vmin=vmin,
                                       vmax=vmax,
                                       transform=geo.projPlane)

    axgr.cbar_axes[0].colorbar(p)  # Adding the colorbar

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

def select_area(data: xr.DataArray, boundValues: np.ndarray):
    """ Select the data in the geographic range that will be plotted """

    [lonW, lonE, latS, latN] = boundValues

    iLonW = np.where(np.isclose(data['longitude'], lonW))[0][0]  # Getting the index for each of the extreme
    iLonE = np.where(np.isclose(data['longitude'], lonE))[0][0]  # values of the latitude and longitude
    iLatS = np.where(np.isclose(data['latitude'], latS))[0][0]
    iLatN = np.where(np.isclose(data['latitude'], latN))[0][0]

    ''' # Remark
    The following part can probably be inproved using xr.DataArray.copy() '''

    res = xr.DataArray(
        data[:, iLatN:iLatS + 1, iLonW:iLonE + 1],  # Selecting the wanted data
        dims=data.dims,
        coords={
            "time": data['time'],
            "latitude": data['latitude'][iLatN:iLatS + 1],  # Adjusting latitude coordinate
            "longitude": data['longitude'][iLonW:iLonE + 1]  # Adjusting longitude coordinate
        }
    )
    return res


def select_time(data: xr.DataArray, timesIndex: np.ndarray) -> xr.DataArray:
    """ Select the data in the time range that will be plotted """

    ''' # Remark
    As above, probable improvment '''

    res = xr.DataArray(
        data.loc[timesIndex, :, :],  # Selecting the wanted data
        dims=data.dims,
        coords={
            "time": timesIndex,  # Adjusting time coordinate
            "latitude": data['latitude'],
            "longitude": data['longitude']
        }
    )
    return res


def select_sample(data: xr.DataArray, boundValues: np.ndarray, timesIndex: np.ndarray) -> xr.DataArray:
    res = select_area(data, boundValues)
    res = select_time(res, timesIndex)
    return res


###   Xarray Operations   ###

def mean_over_time(data: xr.DataArray, span: int, edges: bool = True) -> xr.DataArray:
    if "time" not in data.dims:
        raise ValueError("Le DataArray doit avoir une dimension 'time'.")

    shift = (span - 1) % 2  # Décale d'un cran à droite si span est pair

    if edges:
        rolling_obj = data.rolling(time=span, center=True, min_periods=1)
    else:
        rolling_obj = data.rolling(time=span, center=True, min_periods=span)

    return rolling_obj.construct("window_dim").shift(time=-shift).mean("window_dim")


def sum_over_space(data: xr.DataArray, span: int) -> xr.DataArray:
    res = xr.full_like(data, 0)  # Creating an empty copy
    nbLat = len(data['latitude'])
    nbLon = len(data['longitude'])
    for y in range(nbLat):
        yBegin, yEnd = y - span // 2, y + (span + 1) // 2  # Creating the latitude range for the sum
        if yBegin >= 0 & yEnd <= nbLat:  # Checking if all the latitude indexes to sum exist
            for x in range(nbLon):
                xBegin, xEnd = x - span // 2, x + (span + 1) // 2  # Creating the longitude range for the sum
                if xBegin >= 0 & xEnd <= nbLon:  # Checking if all the longitude indexes to sum exist
                    res[:, y, x] = data[:, yBegin:yEnd, xBegin:xEnd].sum(
                        dim=["latitude", "longitude"]
                    )
                else:
                    res[:, y, x] = None
        else:
            res[:, y, :] = np.zeros_like(data['tp24'][:, y, :]).fill(None)
    return res


def mean_over_space(data: xr.DataArray, span: int) -> xr.DataArray:
    res = xr.full_like(data, 0)  # Creating an empty copy
    nbLat = len(data['latitude'])
    nbLon = len(data['longitude'])
    for y in range(nbLat):
        yBegin, yEnd = y - span // 2, y + (span + 1) // 2  # Creating the latitude range for the mean
        for x in range(nbLon):
            xBegin, xEnd = x - span // 2, x + (span + 1) // 2  # Creating the longitude range for the mean
            res[:, y, x] = data[:, yBegin:yEnd, xBegin:xEnd].mean(
                dim=["latitude", "longitude"]
            )
    return res


###   Day number to date   ###

def date_as_int(date: np.datetime64) -> int:
    """ change a numpy datetime into day's number since 1970-01-01 """
    return date.astype('datetime64[D]').astype(int)


def nb_to_date(nb: int, year: str) -> str:
    dayNum = str(nb)
    dayNum.rjust(3 + len(dayNum), '0')
    res = datetime.strptime(year + "-" + dayNum, "%Y-%j").strftime("%d-%m-%Y")
    return res


def nb_to_numpy_date(nb: int, year: str) -> np.datetime64:
    return np.datetime64(year + '-01-01') + np.timedelta64(nb, 'D')


def get_day_number(date: np.datetime64):
    year = np.datetime_as_string(date.astype('datetime64[Y]'))
    return (date - np.datetime64(year + '-01-01')).astype(int)


###   Mosaic Split : give the best mosaic for a given day list

def mosaic_split(nbMaps: int) -> tuple[int, int]:
    nbRow = 1
    while True:
        """ The loop ends because nbRow grows strictly and 
        for nbRow==nbMaps the condition is valid """
        nbColumn = nbMaps // nbRow + (nbMaps % nbRow > 0)
        if nbColumn - nbRow <= 1:
            return nbRow, nbColumn
        nbRow += 1


###   Handle Directories

def reindex_hindcast(da: xr.DataArray):
    """ Reindexing the ('hdate','time') dimension for hincast files """
    da = da.stack(fullTime=["hdate", "time"])  # Combining the 2 time related coordinates
    newIndexes = []
    for (hdate, time) in da['fullTime'].values:  # Creating the new indexes
        yearOffset = time.year - hdate // 10000
        newIndexes.append(np.datetime64(time) - np.timedelta64(yearOffset, 'Y'))
    reindexed_da = xr.DataArray(
        da.values,
        dims=("latitude", "longitude", "time"),
        coords={
            "latitude": da['latitude'],
            "longitude": da['longitude'],
            "time": np.array(newIndexes)
        }
    )
    return reindexed_da


###   Reindexing hindcasts

def extract_files(
        sourceDir: str,
        pathsToFiles: dict[tuple, str],
):
    fileType = ''
    pathScatter = sourceDir.split('/')
    while pathScatter:
        subDir = pathScatter.pop()
        if subDir == 'daily':
            fileType = pathScatter[-1].split('-')[0]
            break
    assert type != '', "Wrong directory"
    for filename in os.listdir(sourceDir):
        pathsToFiles[(fileType, filename[:-3])] = os.path.join(sourceDir, filename)


###   Correlation

def pears(arr):
    """Compute the Pearson correlation coefficient"""
    arr = arr[np.where(ma.masked_invalid(arr).mask == False)[0]]
    arr = np.array([arr, np.arange(1, len(arr) + 1)])
    return np.corrcoef(arr)[0][1]


def pears_distrib(arr):
    df = pd.DataFrame(arr.T)
    corr = df.corr().values
    return corr[np.triu_indices(corr.shape[0], k=1)]


def pears_norm(arr):
    """Compute the correlation matrix"""
    corr_mat = np.corrcoef(arr)
    return np.linalg.norm(corr_mat)


def pears_mean(arr):
    corr_mat = np.corrcoef(arr)
    return (corr_mat - np.identity(corr_mat.shape[0])).mean()


def pears_full(arr):
    correl_mat = ma.corrcoef(ma.masked_array(arr))
    norm = np.linalg.norm(correl_mat)
    mean = np.mean(correl_mat)
    std = np.std(correl_mat)
    norm_stand = norm / correl_mat.shape[0]
    return np.array([norm, mean, std, norm_stand])


def pearson_correlation(
        data: xr.DataArray,
        func: str = 'full'
) -> xr.DataArray:
    data = data.stack(coordinates=["latitude", "longitude"])
    funcDict = dict(norm=pears_norm, mean=pears_mean, full=pears_full)
    if func == 'full':
        output_dims = [["statistics"]]
    else:
        output_dims = [[]]
    result = xr.apply_ufunc(
        funcDict[func], data,
        input_core_dims=[["number", "coordinates"]],
        output_core_dims=output_dims,
        vectorize=True,
        dask="parallelized"
    )
    if func == 'full':
        result['statistics'] = np.array(['norm', 'mean', 'std', 'norm_stand'])
    return result
