
import os
os.environ["OPENBLAS_NUM_THREADS"] = "4"
import xarray as xr


folder = '/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/continuous-format/daily/tp24'

file_queue = os.listdir(folder)

file = xr.open_dataarray(
    os.path.join(folder, file_queue.pop())
)
res = file.sel(
    latitude=slice(62.5,60.5),
    longitude=slice(9,11.5)
).mean(
    dim=['latitude', 'longitude']
).drop_vars(
    "number", errors="ignore"
)

while file_queue:
    arr = xr.open_dataarray(
        os.path.join(folder, file_queue.pop())
    ).sel(
        latitude=slice(62.5,60.5),
        longitude=slice(9,11.5)
    ).mean(
        dim=['latitude', 'longitude']
    ).drop_vars(
        "number", errors="ignore"
    )
    res = xr.concat(
        [res, arr],
        dim="time"
    ) * 1000

res.to_netcdf("data/rea_raw.nc")
