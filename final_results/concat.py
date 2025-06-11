#
# Concatenate the data from separated months
#

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import xarray as xr


arrays = []

arrays.append(
    xr.open_dataarray(
        'months/may/maxs_corrected_2.nc'
    )
)
arrays.append(
    xr.open_dataarray(
        'months/june/maxs_corrected_3.nc'
    )
)
arrays.append(
    xr.open_dataarray(
        'months/july/maxs_corrected_2.nc'
    )
)
arrays.append(
    xr.open_dataarray(
        'months/august/maxs_corrected_3.nc'
    )
)
arrays.append(
    xr.open_dataarray(
        'months/september/maxs_corrected_3.nc'
    )
)
arrays.append(
    xr.open_dataarray(
        'months/october/maxs_corrected_2.nc'
    )
)

res = xr.concat(
    arrays,
    dim="date"
)
res.to_netcdf("final_results/corrected_data.nc")