#
# Given the data computed in "worst_event_simulated.py", we plot the distribution of those events during the summer
# months (July, August and September).
#
# We use the data averaged over 3 days since this one carry much more information regarding on rare events.
#

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pickle

from weatherdata.classes import Weatherset


# Access the data
with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_all-res.pkl', 'rb') as inp:
    tpSet: Weatherset = pickle.load(inp)
data = xr.open_dataarray(
    tpSet.compute['s2s-HA_avg-all_res-worst_event_simulated-mean3']
)

months = ['July', 'August', 'September']
monthsNb = np.arange(6,9,1)



###############################################################
#
#       Function
#

def plot_distribution(
        arr: xr.DataArray,
        step: str | None = 0.001
):
    """
    Plots the statistical distribution of the data.
    The data is regrouped into nearest values with a step of 1 mm.

    Parameters:
    data (xr.DataArray): Input data with dimensions "years" and coordinates as strings.
    """

    for idx, month in enumerate(months):

        vals = arr.where(arr['olMonth'] == monthsNb[idx], drop=True)

        # Define bin edges with a step of 0.001
        bin_edges = np.arange(np.nanmin(vals), np.nanmax(vals) + step, step)

        # Plot histogram
        plt.figure(figsize=(10, 6))
        plt.hist(vals, bins=bin_edges, edgecolor='black', alpha=0.7)

        # Plot Hans threshold
        with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/continuous_0.5.pkl', 'rb') as era5:
            hansVal = xr.open_dataarray(
                pickle.load(era5).compute['continuous_hans-area-avg-mean3_0.5_monthly-max']
            ).sel(
                years='2023', months='aug'
            ).values
        plt.axvline(x=hansVal, color='red', linestyle='--')
        plt.text(hansVal, 8e2, "Hans", ha='right', va='bottom', color='red', rotation=90)

        plt.xlabel('Precipitations (m)')
        plt.yscale('log')
        plt.ylim([8e-1, 2e3])
        plt.title("Distribution of worst simulated events in " + month)
        plt.grid(True, linestyle='--', alpha=0.6)

        plt.savefig('/nird/projects/NS9873K/emile/unseen-storm-forecasts/plots/simulations_maximums/'
                    'HA_avg-maxs_distribution_'+month+'-mean3.png')

        plt.close()

    pass


###############################################################
#
#       Running the program
#

if __name__ == '__main__':

    globals()['plot_distribution'](
        data
    )