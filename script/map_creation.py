###
###    Creation of Hans Storm weather maps
###

from datetime import datetime

import matplotlib.pyplot as plt
import xarray as xr
from cartopy import crs as ccrs, feature as cfeature



def nbToDate(nb: int) -> str:
    day_num = str(nb)
    day_num.rjust(3 + len(day_num), '0')
    year = '2023'
    res = datetime.strptime(year + "-" + day_num, "%Y-%j").strftime("%m-%d-%Y")
    return res


###     Map creation functions

def map_creator(data: xr.DataArray) -> tuple:
    projPlane = ccrs.PlateCarree()
    projMerc = ccrs.Mercator()
    
    latS = max(57, data['tp24'].GRIB_latitudeOfLastGridPointInDegrees)
    latN = min(66, data['tp24'].GRIB_latitudeOfFirstGridPointInDegrees)
    lonW = max(3, data['tp24'].GRIB_longitudeOfFirstGridPointInDegrees)
    lonE = min(17, data['tp24'].GRIB_longitudeOfLastGridPointInDegrees)
    
    fig = plt.figure(figsize=(15, 10))
    ax = plt.subplot(1, 1, 1, projection=projMerc)
    ax.set_extent([lonW, lonE, latS, latN], crs=projPlane)
    ax.coastlines()
    ax.add_feature(cfeature.STATES, linewidth=0.3, linestyle='--', edgecolor='black')
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle='solid', edgecolor='black')
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.RIVERS)
    
    return fig, ax


def mapping_1d(pathToFile: str, day: int) -> None:
    """ Plot the precipitation data storred on the file entered as argument """
    
    assert (pathToFile.endswith('.nc')), "The file must be in .nc format."
    assert (
        pathToFile.startswith(
            '/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/continuous-format/daily/tp24/'
        )), "The file must be an ERA5 reanalysis data"
    
    data = xr.open_dataarray(pathToFile)
    
    # Creating the map
    fig, ax = map_creator(data)
    ax.set_title('Averaged daily precipitations on ' + nbToDate(day))
    
    # Processing the data
    
    tp = xr.DataArray(
        data['tp24'][[day - 1, day, day + 1], :, :], dims=("time", "latitude", "longitude"),
        coords={"latitude":data['latitude'][:], "longitude":data['longitude'][:]}
    )
    
    # 1 day
    tpPlot1d = ax.contourf(tp['longitude'], tp['latitude'], tp.isel(time=1), transform=ccrs.PlateCarree())
    plt.colorbar(tpPlot1d)
    plt.savefig('unseen-storm-forecasts/maps/1d_tp/1d_tp_' + nbToDate(day))


def mapping_avg_3d(pathToFile: str, day: int) -> None:
    """ Plot the precipitation data storred on the file entered as argument """
    
    assert pathToFile.endswith('.nc'), "The file must be in .nc format."
    assert (
        pathToFile.startswith(
            '/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/continuous-format/daily/tp24/'
        )), "The file must be an ERA5 reanalysis data"
    
    data = xr.open_dataarray(pathToFile)
    
    # Creating the map
    
    fig, ax = map_creator(data)
    ax.set_title('Averaged daily precipitations between ' + nbToDate(day - 1) + ' to ' + nbToDate(day + 1))
    
    # Processing the data
    
    tp = xr.DataArray(
        data['tp24'][[day - 1, day, day + 1], :, :], dims=("time", "latitude", "longitude"),
        coords={"latitude":data['latitude'][:], "longitude":data['longitude'][:]}
    )
    
    # Averaged 3 days
    tpPlot3d = ax.contourf(tp['longitude'], tp['latitude'], tp.mean(dim="time"), transform=ccrs.PlateCarree())
    plt.colorbar(tpPlot3d)
    plt.savefig('unseen-storm-forecasts/maps/3d_tp/3d_avgp_' + nbToDate(day))


### Applying

for number in range(217, 223):
    mapping_1d(
        pathToFile="/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/continuous-format/daily/tp24/tp24_0.25x0"
                   ".25_2023.nc",
        day=number
    )
    mapping_avg_3d(
        pathToFile="/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/continuous-format/daily/tp24/tp24_0.25x0"
                   ".25_2023.nc",
        day=number
    )
    """ mapping_1d(pathToFile="unseen-storm-forecasts/data/continuous/daily/tp24_0.25x0.25_2023.nc", day=number)
    mapping_avg_3d(pathToFile="unseen-storm-forecasts/data/continuous/daily/tp24_0.25x0.25_2023.nc", day=number) """

### Short testing

""" mapping_avg_3d(pathToFile="unseen-storm-forecasts/data/continuous/daily/tp24_0.25x0.25_2023.nc", day=219) """
