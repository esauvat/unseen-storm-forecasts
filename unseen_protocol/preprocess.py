#
# Run some preprocessing over the data, ie: averaging over 3 consecutive days
# and selecting the lead times that are uncorrelated
#

from sys import argv

import xarray as xr
import numpy as np



def rolling_by_htime_group(group, winSpan: int = 3):
    #
    # The function was written by chatGPT
    #

    # Get sorted indices by htime (just in case)
    sorter = np.argsort(group['htime'].values)

    # Sort group by htime
    group_sorted = group.isel(time=sorter)
    htime_sorted = group_sorted['htime']

    # We'll apply rolling manually along the 'time' axis
    values = group_sorted.values
    rolled = np.full_like(values, np.nan)

    # Looping over each time index to compute rolling mean
    for i in range(0, len(htime_sorted)-winSpan):
        # Get window of size winSpan expanding on the right
        window = values[..., i:i+winSpan]
        if window.shape[-1] == winSpan:
            rolled[..., i] = np.nanmean(window, axis=-1)

    # Put the rolled data back into a DataArray
    result = group_sorted.copy(data=rolled)
    return result

def rolling_mean_over_htime(
        da: xr.DataArray,
) -> xr.DataArray:
    da = xr.concat([rolling_by_htime_group(grp) for _, grp in da.groupby('fdate')], dim='time')
    return da.sortby('time')

if __name__ == '__main__':

    if len(argv) >= 2 and argv[1] == "hindcast":
        data = xr.open_dataarray('data/retrieved-hindcast.nc')
    elif len(argv) >= 2 and argv[1] == "forecast":
        data = xr.open_dataarray('data/retrieved-forecast.nc')
    else:
        data = xr.open_dataarray('data/retrieved-full.nc')

    res = rolling_mean_over_htime(data)



    res.to_netcdf('data')