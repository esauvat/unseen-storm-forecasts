import xarray as xr

import test_fidelity as fid
import test_stability as stab
import test_independence as ind

vals = xr.open_dataarray("corrected.nc")
vals = vals.sel(
    date=vals.month==10
)
maxs = vals.max(dim="time")
era5 = xr.open_dataarray(
    "../data/processed-rea-2.nc"
)

outputDir = "figures"

rea, mod = fid.main(
    modelled=maxs,
    reanalysis=era5
)
fid.plot(
    rea, mod,
    outputDir, "October"
)

stab.plot_kde_distributions(
    vals, outputDir
)
stab.plot_return_period(
    vals, outputDir
)

corr, interv = ind.correlation(vals)
ind.plot_correlations(
    corr,
    interv,
    outputDir
)