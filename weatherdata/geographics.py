""" A set of tools to generate maps of Norway """

from cartopy import crs as ccrs, feature as cfeature
from cartopy.mpl.geoaxes import GeoAxes
from mpl_toolkits.axes_grid1 import AxesGrid
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
from __init__ import *


###   Some projection variable   ###

projMerc = ccrs.Mercator()
projPlane = ccrs.PlateCarree()
projLCon = ccrs.LambertConformal()

sizes = {
    'small':(8, 5),
    'medium':(15, 10),
    'large':(20, 15),
    'huge':(60, 45)
}

weightsLRes = xr.open_dataarray(
    '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weatherdata/geo_weights-0.5.nc')
weightsHRes = xr.open_dataarray(
    '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weatherdata/geo_weights-0.25.nc')


###   Map background   ###

def map_background(ax: GeoAxes, boundValues=None) -> GeoAxes:
    if boundValues is None:
        boundValues = []
    assert (len(boundValues) in [0, 4]), "The boundValues must be an array of 4 values"  #
    
    if not boundValues.size == 0:
        ax.set_extent(boundValues, crs=projPlane)  # Set the size of the map according to boundValues
    ax.coastlines()
    ax.add_feature(cfeature.STATES, linewidth=0.3, linestyle='--', edgecolor='black')  # Add european countries borders
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle='solid', edgecolor='black')  # Add bordrers
    ax.add_feature(cfeature.LAKES, alpha=0.5)  # Add lakes
    ax.add_feature(cfeature.LAND)  # Add ground mesh
    ax.add_feature(cfeature.RIVERS)  # Add rivers
    
    return ax


def map(n=1, p=1, nbMap=1, size='medium', boundValues=None, proj=projMerc):
    assert (size in sizes.keys()), "The size is incorrect"
    
    figSize = sizes[size]
    
    axesClass = (GeoAxes,
                 dict(projection=proj))  # Create the subplot class
    
    fig = plt.figure(figsize=figSize)  # Initiate figure
    axgr = AxesGrid(
        fig, 111, axes_class=axesClass,
        # We use an AxesGrid instead of regular Axes to use a unique colorbar
        nrows_ncols=(n, p),  # Grid dimensions
        axes_pad=0.7,
        cbar_location='right',
        cbar_mode='single'
    )  # Solo colorbar
    
    for i in range(nbMap):
        map_background(axgr[i], boundValues)  # Putting background in each effective subplot
    
    return fig, axgr


###   Showcasing the data   ###

def showcase_data(
        data: xr.DataArray,
        boundValues: np.ndarray,
        fig: plt.Figure, axgr: AxesGrid,
        nbMap: int | None = 1,
        **kwargs: np.ndarray
) -> tuple:
    extent = kwargs.get('extent', [])

    if 'time' not in data.dims:
        data = data.expand_dims("time").transpose(
            "time", "latitude",
            "longitude"
        )  # If no time dimension, reshape the array to fit the data access later

    timesIndex = kwargs.get(
        'timesIndex',
        data['time']
    )  # Setting the default value for the time selection to all the dataset
    assert ((timesIndex.min() >= data['time'][0]) & (timesIndex.max() <= data['time'][
        -1]))  # Checking if the time selection does not get out of range for the dataset's dimension

    if extent:
        vmin, vmax = extent
    else:
        effectSample = select_sample(
            data, boundValues,
            timesIndex
        )  # Selecting the values of the dataset that will be plotted to determine the best extent for the colorbar
        vmin, vmax = effectSample.min(skipna=True), effectSample.max(skipna=True)  # Computing the range of the colorbar

    _, Y, X = data.dims

    p: object = None

    for i in range(nbMap):
        p = axgr[i].pcolormesh(
            data[X], data[Y], data.loc[timesIndex[i]],
            # Plotting each set of value on the corresponding subplot
            vmin=vmin,
            vmax=vmax,
            transform=projPlane
        )

    axgr.cbar_axes[0].colorbar(p)  # Adding the colorbar

    return fig, axgr


###   Apply earth's curvature weights

def apply_curv_weights(
        data: xr.DataArray | xr.Dataset,
) -> xr.DataArray | xr.Dataset :
    """ Apply weights to take into account earth's curvature when averaging over space """

    resolution = data['latitude'].values[0] - data['latitude'].values[1]
    if resolution == 0.5:
        weights = weightsLRes
    elif resolution == 0.25:
        weights = weightsHRes
    else:
        raise ValueError('The resolution must be 0.5 or 0.25')

    latMin = float(data['latitude'].min().values)
    latMax = float(data['latitude'].max().values)
    lonMin = float(data['longitude'].min().values)
    lonMax = float(data['longitude'].max().values)

    weights = weights.sel(
        latitude=slice(latMax, latMin),
        longitude=slice(lonMin, lonMax)
    )
    if type(data) is xr.Dataset:
        res = data.copy(deep=True)
        for var in data.data_vars:
            res[var] = (data[var] * weights) / weights.max()
    elif type(data) is xr.DataArray:
        res = (data * weights) / weights.max()
    else:
        raise ValueError('The data must be a Dataset or a DataArray')

    return res