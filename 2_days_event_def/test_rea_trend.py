#
# This file aims to test if there is any trending in the reanalysis data, if so,
# it shall correct it to keep a 80 years sample with no trend.
#

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
import datetime



data = xr.open_dataarray('data/retrieved-rea-2.nc')

# August

aug = data.sel(time=data.time['time.month']==8).values
x_val = np.arange(
    1941,
    2024,
    1
)
precip

plt.scatter(years, precip, marker='x', color='red')
plt.xlabel("Years")
plt.ylabel("Precipitations")

# Unbias

def expfunc(x, y, z, s):
    return y * np.exp(-z * x) + s

[p_opt, p_cov] = optimize.curve_fit(expfunc, years-1940, precip, p0=(-1,0,1), maxfev=1000)

plt.plot(years, expfunc(years-1940, *p_opt), 'b',
         label=f'fit:a=%5.3f, b=%5.3f, c=%5.3f'%tuple(p_opt))
plt.legend()
plt.savefig('figures/rea_trend.png')
plt.close()