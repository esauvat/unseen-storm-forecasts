
''' A set of tools to generate maps of Norway '''


from cartopy import crs as ccrs, feature as cfeature
from cartopy.mpl.geoaxes import GeoAxes
from cartopy.vector_transform import vector_scalar_to_grid
from cartopy import config
from matplotlib.axes import Axes
from mpl_toolkits.axes_grid1 import AxesGrid
import matplotlib.pyplot as plt

###   Some projection variable   ###

projMerc = ccrs.Mercator()
projPlane = ccrs.PlateCarree()
projLCon = ccrs.LambertConformal()

sizes = {
    'small':(8,5),
    'medium':(15,10),
    'large':(20,15),
    'huge':(60,45)
}


###   Map background   ###

def map_background(ax:GeoAxes, boundaries:list[int]=[]) -> GeoAxes:

    assert (len(boundaries) in [0,4]) , "The boundaries must be an array of 4 values"           # 

    if not boundaries.size==0 :
        ax.set_extent(boundaries, crs=projPlane)                                                # Set the size of the map according to boundaries
    ax.coastlines()
    ax.add_feature(cfeature.STATES, linewidth=0.3, linestyle='--', edgecolor='black')           # Add european countries borders
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle='solid', edgecolor='black')       # Add bordrers
    ax.add_feature(cfeature.LAKES, alpha=0.5)                                                   # Add lakes
    ax.add_feature(cfeature.LAND)                                                               # Add ground mesh
    ax.add_feature(cfeature.RIVERS)                                                             # Add rivers

    return ax


def map(n=1, p=1, nbMap=1, size='medium', boundaries = None, proj=projMerc) :

    assert (size in sizes.keys()), "The size is incorrect"

    figSize = sizes[size]
    
    axesClass = (GeoAxes,
               dict(projection=proj))                                                           # Create the subplot class
    
    fig = plt.figure(figsize=figSize)                                                           # Initiate figure
    axgr = AxesGrid(fig, 111, axes_class=axesClass,                                             # We use an AxesGrid instead of regular Axes to use a unique colorbar
                    nrows_ncols= (n,p),                                                         # Grid dimensions
                    axes_pad=0.7,
                    cbar_location='right',
                    cbar_mode='single')                                                         # Solo colorbar

    for i in range(nbMap):
        map_background(axgr[i],boundaries)                                                      # Putting background in each effective subplot

    return fig, axgr