#
# Using stochastic gradient descent, we want to get the best
# possible coefficent to correc the dataset for the stability test.
#

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt



def grad(X, y, theta):
    n = X.shape[0]
    return 2 / n * X.T.dot(X.dot(theta) - y)

def gd(X, y, step, nb):
    
    cost_history = []
    
    m = len(X)
    if len(y.shape)==1:
        y = y.reshape((len(y),1))
    
    theta = np.random.randn(2,1)
    
    for i in range(nb):
        theta -= step*grad(X, y, theta)
        if (np.any(np.isnan(theta)) or np.any(np.isinf(theta))): 
            print("Nan or Inf value in theta")
            return [0,0], []
        
        if i%1000 == 0:
            risk = np.nanmean((X.dot(theta)-y)**2)
            cost_history.append(risk)
    
    return theta, cost_history

months = ['may', 'june', 'july', 'august', 'september', 'october']

mod = xr.open_dataarray(
    'data/processed-full.nc'
)
arrays : list[xr.DataArray] = []

for mid, m in enumerate(months):
    path = 'second_correction/'+m+'_diffs.nc'
    da = xr.open_dataarray(path)
    
    res = mod.sel(date=(mod.month==mid+5))
    
    for tid, t in enumerate(res.time.values):
        if not tid==0:
            y = da.sel(var='diff', time=t).values.flatten()
            x = np.zeros((len(y), 2))
            x[:, 0] = da.sel(var='val', time=t).values.flatten()
            x[:, 1] = da.sel(var='val', time=t).values.flatten() ** 2
            y = y[~np.isnan(x[:,1])]
            x = x[~np.isnan(x[:,1])]
        
            theta, costs = gd(x, y, 5e-6, 20000)
    
            vals = res.sel(time=t).values
            res[...,tid] -= theta[0]*vals + theta[1]*vals**2
    
    arrays.append(res)
    
corrected = xr.concat(
    arrays,
    dim='date'
)
corrected.to_netcdf('second_correction/v1/corrected_1.nc')

maxs = corrected.max(dim="time")
maxs.to_netcdf("second_correction/v1/maxs_corrected.nc")


# Testing

import sys
sys.path.append(
    '/nird/projects/NS9873K/emile/unseen-storm-forecasts'
)

import test_stability as stab

stab.plot_kde_distributions(
    corrected, "second_correction/v1"
)
stab.plot_return_period(
    corrected, "second_correction/v1"
)

import test_fidelity as fid

rea, mod = fid.main(
    "second_correction/v1/maxs_corrected.nc"
)
fid.plot(rea, mod)