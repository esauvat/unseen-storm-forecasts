#
# After retrieving the reanalysis data, we need to compute the maximum recorded events
# for each of the targeted months, being the ones between May and October
#

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import xarray as xr
import numpy as np

from weatherdata import sum_over_time



###############################################################
#
#       Functions
#

strDict_months = {
    1:"jan", 2:"feb", 3:"mar", 4:"apr", 5:"may", 6:"jun",
    7:"jul", 8:"aug", 9:"sep", 10:"oct", 11:"nov", 12:"dec"
}


def compute_maxs(
        da_val: xr.DataArray,
        da_res: xr.DataArray,
        month: int,
) -> None:
    """
    Compute the maximum over the specified month for each year of the data.

    :param da_val: DataArray containing the data to be processed.
    
    :param da_res: DataArray of the results, carefull this array will be
        modified in place since it stores the results for each year and months
        between May and October.
        
    :param month: Integer representing the month to compute the maximum over,
        each month is represented by its calendar number (eg: 1 → January).
    """

    years: np.ndarray = np.unique(
        [ date.astype('datetime64[Y]') for date in da_val.time.values ]
    )

    if any(da_res.year.values != years):
        raise ValueError(
            "The years in the value array does not match the one from the results array."
        )
    if not ('year' in da_res.dims and 'month' in da_res.dims):
        raise ValueError(
            f'Wrong dimensions for the results array : {da_res.dims} where it should be ("year", "month")'
        )

    for year in years:
        timeIndexers = xr.DataArray(
            data=np.arange(
                year + np.timedelta64(month - 1, 'M'),
                year + np.timedelta64(month, 'M'),
                np.timedelta64(1, 'D')
            ),
            dims="time"
        )
        da_res.loc[ year, strDict_months[month] ] = da_val.sel(time=timeIndexers).max(dim="time").values

    pass


def main(
        vals: xr.DataArray | None = None
) -> xr.DataArray:
    """
    Compute the monthly maximum for each year on the May-October time period.

    :param vals: DataArray containing the data to be processed, the default one is
        stored in the 'data/retrieved-rea.nc' netCDF file.
    :return: DataArray containing the maximum over the specified month for each year.
    """

    if not vals:
        vals = xr.open_dataarray('data/retrieved-rea.nc')
        
    yearsCoords: np.ndarray = np.arange(
        np.datetime64('1941'),
        np.datetime64('2025'),
        np.timedelta64(1, 'Y')
    )
    monthsCoords: np.ndarray = np.array(
        [strDict_months[ month ] for month in range(5,11)]
    )
    res: xr.DataArray = xr.DataArray(
        data=np.full(shape=(len(yearsCoords), 6), fill_value=np.nan),
        dims=[ "year", "month" ],
        coords=[ yearsCoords, monthsCoords ]
    )

    for month in range(5, 11):
        compute_maxs(
            vals, res, month
        )

    return res


###############################################################
#
#       Running script
#

if __name__ == "__main__":

    main().to_netcdf('data/processed-rea.nc')