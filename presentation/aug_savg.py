import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from typing import cast

import sys
sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/')

from weatherdata.geographics import apply_curv_weights
from weatherdata import sum_over_time

arr = xr.open_dataarray(
    '/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/continuous-format/daily/tp24/tp24_0.5x0.5_2023.nc'
)

arr = apply_curv_weights(
    arr.sel(
        latitude=slice(62.5,60.5),
        longitude=slice(9,11.5)
    )
).mean(dim=["latitude","longitude"])

arr = arr.sel(
    time=slice(
        np.datetime64('2023-08'),
        np.datetime64('2023-08-31')
    )
) * 1000

vals = cast(xr.DataArray, arr).values
dates = arr.time.values

fig, ax = plt.subplots()

ax.plot(dates, vals)
plt.suptitle('Precipitations over Hans area')

major_dates = np.arange(
    dates.min(), dates.max(), np.timedelta64(1, 'W')
)

ax.set_xticks(major_dates)

plt.savefig('presentation/aug.png')