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


def plot_kde_distributions(
        da: xr.DataArray,
        outputDir: str = "results"
):
    """
    Plots KDE distributions of a DataArray with coordinates (date, time).
    
    :param da: Input data with dim date and coords (date, time).
    :param outputDir: Directory to save the plots.
    """

    # Normalize lead times for colormap
    ltValues = da.time.values
    norm = plt.Normalize(vmin=min(ltValues), vmax=max(ltValues)) # type: ignore
    cmap = plt.get_cmap("viridis")

    # Create a plot for each month
    months = ["May", "June", "July", "August", "September", "October"]
    for mId, month in enumerate(months):
        plt.figure(figsize=(10, 6))
        monthData = da.where(da.month == mId+5, drop=True)

        for lt in ltValues:
            # Extract the data for this object
            data = monthData.sel(time=lt).values.flatten()

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
    ltValues = da.time.values
    norm = plt.Normalize(vmin=min(ltValues), vmax=max(ltValues)) # type: ignore
    cmap = plt.get_cmap("viridis")

    # Create a plot for each month
    months = ["May", "June", "July", "August", "September", "October"]
    for mId, month in enumerate(months):
        plt.figure(figsize=(10, 6))
        monthData = da.where(da.month==mId+5, drop=True)

        for lt in ltValues:
            # Extract the data for this object
            data = monthData.sel(time=lt).values.flatten()
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

    
    tp24 = xr.open_dataarray(
            os.path.join('data','processed-full.nc')
    )

    plot_kde_distributions(
        tp24
    )

    plot_return_period(
        tp24
    )