import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from typing import cast
from matplotlib.ticker import MultipleLocator

sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/')
from weatherdata.geographics import apply_curv_weights
from weatherdata import sum_over_time

years = []
maxs = []

dir = '/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/continuous-format/daily/tp24'
for filename in os.listdir(dir):
    if '0.5x0.5' in filename:
        arr = xr.open_dataarray(
            os.path.join(dir, filename)
        )
        arr = cast(
            xr.DataArray,
            apply_curv_weights(
                arr.sel(
                    latitude=slice(62.5,60.5),
                    longitude=slice(9,11.5)
                )
            )
        ).mean(
            dim=['latitude','longitude']
        )
        arr = sum_over_time(
            arr, span=3, edges=True
        )
        
        years.append(int(filename[-7:-3]))
        maxs.append(arr.max().values)
        
years = np.asarray(years)
args = np.argsort(years)

years = years[args]
maxs = np.asarray(maxs)[args] * 1000

fig, ax = plt.subplots()
ax.scatter(years, maxs)

# Set major ticks every decade
major_years = np.arange((years.min() // 10 + 1) * 10, years.max() + 1, 10)
ax.set_xticks(major_years, labels=major_years.astype(str), rotation=45)

# # Set minor ticks every year
# ax.set_xticks(np.arange(years.min(), years.max() + 1), minor=True)

plt.suptitle('Maximums accumulated precipitations')

plt.savefig(
    '/nird/projects/NS9873K/emile/unseen-storm-forecasts/presentation/maxs.png'
)