
###   
###    Creation of Hans Storm weather maps
###

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from netCDF4 import Dataset
from cartopy import crs as ccrs, feature as cfeature
from datetime import datetime

def nbToDate(nb : int) -> str :
    day_num = str(nb)
    day_num.rjust(3 + len(day_num), '0')
    year='2023'
    res = datetime.strptime(year + "-" + day_num, "%Y-%j").strftime("%m-%d-%Y")
    return res


###     Map creation functions

def map_creator(data : Dataset) -> tuple :

    projPlane = ccrs.PlateCarree()

    latS = max(57.1, data['tp24'].GRIB_latitudeOfFirstGridPointInDegrees)
    latN = min(71.2, data['tp24'].GRIB_latitudeOfLastridPointInDegrees)
    lonW = max(3.1, data['tp24'].GRIB_longitudeOfFirstGridPointInDegrees)
    lonE = min(31.3, data['tp24'].GRIB_longitudeOfLastGridPointInDegrees)
    cLat = (latS + latN) / 2
    cLon = (lonW + lonE) / 2

    cities_mask = cfeature.NaturalEarthFeature(
        'cultural',
        'Populated Places',
        scale = '50m',
    )
 
    fig = plt.figure(figsize=(10,10))
    ax = plt.subplot(1, 1, 1, projPlane)
    ax.set_extent([lonW, lonE, latS, latN], crs=projPlane)
    ax.coastlines()
    ax.add_feature(cfeature.STATES, linewidth=0.3, linestyle='--', edgecolor='black')
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle='solid', edgecolor='black')
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.RIVERS)
    ax.add_feature(cities_mask)



def mapping(pathToFile : str, day : int) -> None :

    ''' Plot the precipitation data storred on the file entered as argument '''

    assert(pathToFile.endswith('.nc'))
    ("The file must be in .nc format.")
    assert(pathToFile.startswith('/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/continuous-format/daily/tp24/'))
    ("The file must be an ERA5 reanalysis data")

    data = Dataset(pathToFile, 'r')

    # Creating the maps
    fig, ax = map_creator(data)    
    ax.set_title('Averaged daily precipitations on ' + nbToDate(day))

    fig2, ax2 = map_creator(data)
    ax.set_title('Averaged daily precipitations between 0 ' + nbToDate(day-1) + ' to ' + nbToDate(day+1))


    # Processing the data

    tp = xr.DataArray(data['tp24'][[day-1,day,day+1],:,:], dims=("time", "latitude", "longitude"), coords={"latitude":data['latitude'][:], "longitude":data['longitude'][:]})

        # 1 day
    tpPlot1d = ax.contourf(tp['latitude'], tp['longitude'], tp.isel(time=1), transform=ccrs.PlateCarree())
    plt.colorbar(tpPlot1d)
    plt.savefig('maps/tp_1d_'+nbToDate(day))

        # Averaged 3 days
    tpPlot3d = ax2.contourf(tp['latitude'], tp['longitude'], tp.mean(dim="time"), transform=ccrs.PlateCarree())
    plt.colorbar(tpPlot3d)
    plt.savefig('maps/tp_3d_'+nbToDate(day))



### Applying

for number in range(217,223):
    mapping(pathToFile="/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/continuous-format/daily/tp24/tp24_0.25x0.25_2023.nc", day=number)
    