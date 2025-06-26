import xarray as xr
import numpy as np
import scipy.optimize as optimize


processed = xr.open_dataarray("../data/processed.nc")
processed = processed.sel(
    date=processed.month==7
)
maxs = processed.max(dim="time")

stacked = processed.copy().stack(
    d=["date", "number"]
).reset_index('d').drop_vars(
    ["date", "number", "month"]
)
vals = stacked.values
vals = vals[:, ~np.isnan(vals[0])]
vals_sorted = np.sort(vals, axis=1)
refs = np.sort(vals[0], axis=-1)
vals_diffs = (vals_sorted - refs)
diffs = xr.DataArray(
    data=np.array([vals_sorted, vals_diffs]),
    dims=("var",) + stacked.dims,
    coords=dict(
        var=["val", "diff"],
        time=stacked.time
    )
)

def polyfunc(x, a, b, c):
    return a * x**2 + b * x + c
def expfunc(x, a, b, c):
    return a * np.exp(-b * x) + c

corrected = processed.copy()
for tid, t in enumerate(corrected.time.values):
    y = diffs.sel(var="diff", time=t).values
    x = diffs.sel(var="val", time=t).values

    [p_opt, p_cov] = optimize.curve_fit(polyfunc, x, y, p0=(0,0,0))

    vals = corrected.sel(time=t).values
    corrected[...,tid] -= polyfunc(vals, *p_opt)

corrected.to_netcdf("corrected.nc")