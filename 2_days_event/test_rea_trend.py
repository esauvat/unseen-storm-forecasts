#
# This file aims to test if there is any trending in the reanalysis data, if so,
# it shall correct it to keep a 80 years sample with no trend.
#

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize



data = xr.open_dataarray('data/processed-rea-2.nc')

# August

aug = data.sel(month='aug').values
years = np.arange(
    1941,
    2025,
    1
)

plt.scatter(years, aug, marker='x', color='red')
plt.xlabel("Years")
plt.ylabel("Precipitations")

# Unbias

def expfunc(x, y, z, s):
    return y * np.exp(-z * x) + s

def polyfunc(x, b, c):
    return b * x + c

[p_opt, p_cov] = optimize.curve_fit(polyfunc, years-1940, aug, p0=(0,0))

plt.plot(years, polyfunc(years-1940, *p_opt), 'b',
         label=f'fit: b=%5.3f, c=%5.3f'%tuple(p_opt))
plt.legend()
plt.savefig('rea_trend.png')
plt.close()