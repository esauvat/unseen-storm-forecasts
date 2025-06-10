#
# Correct the stability test by applying a multiplicative factor for each lead time
#

import numpy as np
import xarray as xr
import sys
sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts')
import test_stability as stab



data = xr.open_dataarray('data/processed-full.nc')

def process_month(m: int) :
    mData = data.sel(date=(data.month==m))
    res = xr.full_like(mData, 1)
    for i in range(1,len(res.time.values)):
        res[...,i] = mData[...,i] / mData[...,0]
    return res

def get_med(m: int):
    res = []
    arr = process_month(m)
    for t in arr.time.values:
        vals = arr.sel(time=t).values.flatten()
        vals = vals[~np.isnan(vals)]
        # vals = vals[~np.isinf(vals)]
        res.append(np.median(vals))
    return np.asarray(res)

arrays = []

for month in range(5,11):
    factors = get_med(month)
    mData = data.sel(date=data.month==month)
    for tid in range(len(data.time.values)):
        mData[...,tid] /= factors[tid]
    arrays.append(mData)

corrected = xr.concat(
    arrays,
    dim='date'
)

stab.plot_kde_distributions(
    corrected, "/nird/projects/NS9873K/emile/unseen-storm-forecasts/first_correction"
)

stab.plot_return_period(
    corrected, "/nird/projects/NS9873K/emile/unseen-storm-forecasts/first_correction"
)