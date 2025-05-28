#
# The stability test aims to assess the non-drifting of the model over time.
# To do so we plot the distribution of the data and the estimated return period
# associated with precipitation amounts for each lead times.
#

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from numpy.typing import NDArray



###############################################################
#
#       Functions
#

def preprocess(
        da: xr.DataArray,
) -> xr.DataArray:
    """
    Flatten the DataArray, keeping only a leadtime and time coordinates on one dimension.
    
    Argument:
        da (DataArray) : DataArray with dimensions ("date", "number", "time")
    
    Return: 
        DataArray with dimensions ("date", "lead_time")
    """

    timeShifts = np.array([
        np.timedelta64(n, 'ms')
        for n in range(len(da.number.values) * len(da.time.values))
    ])
    
    newDates = np.concat(
        [
            timeShifts + date
            for date in da.date.values
        ],
        axis=-1
    )
    newLT = np.concat(
        [
            da.time.values
            for _ in range(len(da.date.values)*len(da.number.values))
        ],
        axis=-1
    )
    
    res = xr.DataArray(
        data = da.values.flatten(),
        dims = ("date"),
        coords={
            "date": ("date", newDates),
            "lead_time": ("date", newLT)
        }
    )
    
    return res


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
        srcArray = da.where(da.date['date.month']==mId, drop=True)
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
    ).transpose("month","ltime","date")


def plot_kde_distributions(
        da: xr.DataArray,
        outputDir: str = "results"
):
    """
    Plots KDE distributions of a DataArray with coordinates (date, lead_time).
    
    :param da: Input data with dim date and coords (date, lead_time).
    :param outputDir: Directory to save the plots.
    """

    # Normalize lead times for colormap
    ltValues = np.unique(da.lead_time.values)
    norm = plt.Normalize(vmin=min(ltValues), vmax=max(ltValues)) # type: ignore
    cmap = plt.get_cmap("viridis")

    # Create a plot for each month
    months = ["May", "June", "July", "August", "September", "October"]
    for mId, month in enumerate(months):
        plt.figure(figsize=(10, 6))
        monthData = da.where(da.date['date.month']==mId+5, drop=True)

        for lt in ltValues:
            # Extract the data for this object
            data = monthData.where(monthData.lead_time==lt, drop=True).values

            # Transparency: low alpha normally, full alpha for every 5th curve
            alpha = 1.0 if ((43-lt) % 4 == 0) else 0.1

            # Compute color from colormap
            color = cmap(norm(lt))

            # Plot using seaborn kdeplot
            sns.kdeplot(data, alpha=alpha, color=color, label=f'Lead time {lt}' if ((43-lt) % 4 == 0) else None, warn_singular=False)

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

    :param da: Input data with dims (date) and coordinates ("date", "lead_time").
    :param outputDir: Directory to save the plots.
    """

    # Normalize lead times for colormap
    ltValues = np.unique(da.lead_time.values)
    norm = plt.Normalize(vmin=min(ltValues), vmax=max(ltValues)) # type: ignore
    cmap = plt.get_cmap("viridis")

    # Create a plot for each month
    months = ["May", "June", "July", "August", "September", "October"]
    for mId, month in enumerate(months):
        plt.figure(figsize=(10, 6))
        monthData = da.where(da.date['date.month']==mId+5, drop=True)

        for lt in ltValues:
            # Extract the data for this object
            data = monthData.where(monthData.lead_time==lt).values
            data = data[~np.isnan(data)]

            # Sort in descending order
            sorted_data = np.sort(data)[::-1]
            n = len(sorted_data)

            # Compute the return period
            ranks = np.arange(1,n+1)
            return_period = (n+1) / ranks

            # Transparency: low alpha normally, full alpha for every 5th curve
            alpha = 1.0 if ((43-lt) % 4 == 0) else 0.1

            # Compute color from colormap
            color = cmap(norm(lt))

            # Plot
            plt.plot(sorted_data, return_period, alpha=alpha, color=color, label=f'Lead time {lt}' if ((43-lt) % 4 == 0) else None)

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

    
    tp24 = preprocess(
        xr.open_dataarray(
            os.path.join('data','retrieved-full.nc')
        )
    )

    plot_kde_distributions(
        tp24
    )

    plot_return_period(
        tp24
    )