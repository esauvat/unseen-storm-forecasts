#
# The stability test aims to assess the non-drifting of the model over time.
# To do so we plot the distribution of the data and the estimated return period
# associated with precipitation amounts for each lead times.
#

import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from numpy.typing import NDArray



###############################################################
#
#       Functions
#

def preprocess(
        da: xr.DataArray,
) -> xr.DataArray:
    """
    Flatten the DataArray, keeping only a leadtime and time coordinates.
    """

    da = da.stack(obj=["idate", "time", "number"]).rename(
        {"time":"lead_time"}
    )
    hdate_to_dt = (
        lambda d : np.datetime64(
                "-".join([str(d)[:4], str(d)[4:6], str(d)[6:]])
            )
        )

    timeShifts: NDArray = np.array(
            [
                [np.timedelta64(d, 'D') + np.timedelta64(ns, 'ns')
                for ns in np.unique(da.number.values)]
                for d in np.unique(da.lead_time.values).astype(int)
            ]
        ).flatten()

    idateRepeatAdd = xr.DataArray(
        np.zeros(len(np.unique(da.hdate.values))),
        coords = [("hdate", np.unique(da.hdate.values))]
    )

    newTimes: list = []

    idateIdx = np.unique(
        pd.MultiIndex.from_arrays(
            [da.hdate.values, da.fdate.values]
        )
    )
    for (hd, _) in idateIdx:
        addon = int(idateRepeatAdd.sel(hdate=hd).values)
        idateRepeatAdd.loc[hd] = addon + 1
        newTimes.append(
            hdate_to_dt(hd) + np.timedelta64(addon, 's') + timeShifts
        )

    newTimes = np.array(newTimes).flatten()

    return da.reset_index("obj").drop_vars(
        ["number", "idate", "fdate", "hdate"]
    ).rename(
        { "obj":"time" }
    ).assign_coords(
        time=newTimes
    )


# arr = xr.open_dataarray('data/retrieved-full.nc')
# res = preprocess(arr)

def distribution(
        da: xr.DataArray
) -> xr.DataArray:
    """
    Compute the distribution of the simulated data for each lead time.
    We separate them by month.
    """

    months = [
        "May", "June", "July", "August", "September", "October"
    ]
    ltimes = np.unique(da.lead_time.values.astype(int))

    arrays: list = []

    for mId, month in enumerate(months):
        mId += 5
        mArrs: list = []
        srcArray = da.where(da.time['time.month']==mId, drop=True)
        for lt in ltimes:
            mArrs.append(
                srcArray.where(
                    srcArray.lead_time==lt, drop=True
                ).drop_vars("lead_time").expand_dims(
                    {"ltime":[lt]}
                )
            )
        arrays.append(
            xr.concat(mArrs, dim="ltime").expand_dims(
                {"month":[month]}
            )
        )

    return xr.concat(
        arrays,
        dim="month"
    ).rename(
        {"time":"obj"}
    ).transpose("month","ltime","obj")


def plot_kde_distributions(
        da: xr.DataArray,
        outputDir: str = "results"
):
    """
    Plots KDE distributions of a DataArray with dims (month, ltime, object).
    
    :param da: Input data with dims (month, ltime, object).
    :param outputDir: Directory to save the plots.
    """

    # Check required dimensions
    if not all(dim in da.dims for dim in ['month', 'ltime', 'obj']):
        raise ValueError("Input DataArray must have dimensions: 'month', 'ltime', 'obj'.")

    # Normalize lead times for colormap
    ltValues = da.ltime.values
    norm = plt.Normalize(vmin=min(ltValues), vmax=max(ltValues))
    cmap = plt.get_cmap("viridis")

    # Create a plot for each month
    for month in da.month.values:
        plt.figure(figsize=(10, 6))
        monthData = da.sel(month=month)

        for lt in da.ltime.values:
            # Extract the data for this object
            data = monthData.sel(ltime=lt).values

            # Transparency: low alpha normally, full alpha for every 5th curve
            alpha = 1.0 if ((43-lt) % 5 == 0) else 0.1

            # Compute color from colormap
            color = cmap(norm(lt))

            # Plot using seaborn kdeplot
            sns.kdeplot(data, alpha=alpha, color=color, label=f'Lead time {lt}' if ((43-lt) % 5 == 0) else None, warn_singular=False)

        plt.title(f'KDE Distributions for {month}')
        plt.xlabel('Precipitations')
        # plt.xlim(-0.003,0.017)
        plt.ylabel('Density')
        plt.legend()
        plt.grid(True)

        # Save plot
        filename = os.path.join(outputDir, f'stability_kde-{month}.png')
        plt.savefig(filename)
        plt.close()  # Close the figure to save memory

    pass


def plot_return_period(
        da: xr.DataArray,
        outputDir: str = "results"
):
    """
    Plot the return period of precipitation events.

    :param da: Input data with dims (month, ltime, object).
    :param outputDir: Directory to save the plots.
    """

    # Check required dimensions
    if not all(dim in da.dims for dim in [ 'month', 'ltime', 'obj' ]):
        raise ValueError("Input DataArray must have dimensions: 'month', 'ltime', 'obj'.")

    # Normalize lead times for colormap
    ltValues = da.ltime.values
    norm = plt.Normalize(vmin=min(ltValues), vmax=max(ltValues))
    cmap = plt.get_cmap("viridis")

    # Create a plot for each month
    for month in da.month.values:
        plt.figure(figsize=(10, 6))
        monthData = da.sel(month=month)

        for lt in da.ltime.values:
            # Extract the data for this object
            data = monthData.sel(ltime=lt).values
            data = data[~np.isnan(data)]

            # Sort in descending order
            sorted_data = np.sort(data)[::-1]
            n = len(sorted_data)

            # Compute the return period
            ranks = np.arange(1,n+1)
            return_period = (n+1) / ranks

            # Transparency: low alpha normally, full alpha for every 5th curve
            alpha = 1.0 if ((43-lt) % 5 == 0) else 0.1

            # Compute color from colormap
            color = cmap(norm(lt))

            # Plot
            plt.plot(sorted_data, return_period, alpha=alpha, color=color, label=f'Lead time {lt}' if ((43-lt) % 5 == 0) else None)

        plt.title(f'Return periods for {month}')
        plt.xlabel('Precipitations')
        plt.yscale('log')
        plt.legend()
        plt.grid(True)

        # Save plot
        filename = os.path.join(outputDir, f'stability_retper-{month}.png')
        plt.savefig(filename)
        plt.close()  # Close the figure to save memory

    pass



###############################################################
#
#       Running script
#

if __name__ == "__main__":

    if not 'time-stacked-full.nc' in os.listdir('data'):
        tp24 = preprocess(
            xr.open_dataarray(
                os.path.join('data','retrieved-full.nc')
            )
        )
        tp24.to_netcdf(os.path.join('data','time-stacked-full.nc'))
    else:
        tp24 = xr.open_dataarray(
            os.path.join('data','time-stacked-full.nc')
        )

    distrib = distribution(tp24)

    plot_kde_distributions(
        distrib
    )

    plot_return_period(
        distrib
    )