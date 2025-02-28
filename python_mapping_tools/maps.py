
''' A set of tools to generate maps of Norway '''


from cartopy import crs as ccrs, feature as cfeature
from cartopy.mpl.geoaxes import GeoAxes
from cartopy.vector_transform import vector_scalar_to_grid
from cartopy import config
from matplotlib.axes import Axes
from mpl_toolkits.axes_grid1 import AxesGrid
import matplotlib.pyplot as plt
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

###   Some projection variable   ###

projMerc = ccrs.Mercator()
projPlane = ccrs.PlateCarree()
projLCon = ccrs.LambertConformal()

sizes = {
    'small':(8,5),
    'medium':(15,10),
    'large':(20,15)
}


###   Map background   ###

# def map(n=1, p=1, x=1, boundaries = None, proj=projMerc) -> plt.Axes :
def map_background(ax:GeoAxes, boundaries=[]) :

    assert(len(boundaries)==4 or boundaries.size==0)
    ("The boundaries must be an array of 4 values")

    # ax = plt.subplot(n, p, x, projection = proj)
    if not boundaries.size==0 :
        ax.set_extent(boundaries, crs=projPlane)
    ax.coastlines()
    ax.add_feature(cfeature.STATES, linewidth=0.3, linestyle='--', edgecolor='black')
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle='solid', edgecolor='black')
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.RIVERS)

    return ax


def map(n=1, p=1, size='medium', boundaries = None, proj=projPlane) :

    assert((size in sizes.keys()))

    figSize = sizes[size]

    if n==1 & p==1:
        fig, ax = plt.subplot(n, p, 1, figure=plt.figure(figsize=figSize), projection=proj)
        map_background(ax,boundaries)

        return fig, ax
    
    axesClass = (GeoAxes,
               dict(projection=proj))
    
    fig = plt.figure(figsize=figSize)
    axgr = AxesGrid(fig, 111, axes_class=axesClass,
                    nrows_ncols= (n,p), 
                    axes_pad=0.7,
                    cbar_location='right',
                    cbar_mode='single')

    for ax in axgr:
        map_background(ax,boundaries)

    return fig, axgr
