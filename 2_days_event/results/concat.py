import xarray as xr
import os


arrays = []

for folder in [
    "may", "june", "july", "august", "september", "october"
]:
    arrays.append(
        xr.open_dataarray(
            os.path.join("../", folder, "corrected.nc"),
            engine="netcdf4"
        )
    )

xr.concat(arrays, dim="date").to_netcdf(
    "../data/2_days_corrected.nc"
)