#
# Plotting script to explore the variations between hindcast and forecast results
#
from typing import Callable

import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import scipy.stats as stats



###############################################################
#
#   Retrieving the data
#

sameType: list[xr.DataArray] = []
diffType: list[xr.DataArray] = []

for dataType in ['forecast', 'hindcast']:
    for averaging in [2, 3]:
        da = xr.open_dataarray(
            ('/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/'
            + dataType + '_results/s2s-' + dataType +
            '-HA_avg-all_res-worst_event_simulated-mean' + str(averaging) + '.nc')
        ).expand_dims(
            {"avg" : [averaging]}
        )
        sameType.append(da)
    diffType.append(
        xr.concat(
            sameType,
            dim="avg"
        ).expand_dims(
            {"dataType" : [dataType]},
        )
    )
    sameType = []



###############################################################
#
#   Pre-process
#

processed: list[ xr.DataArray ] = [ ]

months: list[ str ] = [
    'jan', 'feb', 'mar', 'apr', 'may', 'jun',
    'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
]
statsFunc: dict[ str, Callable ] = {
    "mean":np.mean, "std":np.std,
    "skew":stats.skew, "kurt":stats.kurtosis,
}

for da in diffType:
    # For loop to treat forecast and hindcast
    tList = []

    for mIdx, month in enumerate(months):
        # For loop to get each month, can't be concatenated because the dimensions are inhomogenous
        mList = []

        for stat in statsFunc.keys():
        # For loop to apply each of the statistical functions

            s_da = da.where(
                da.olMonth == (mIdx+1), drop=True
            ).reduce(
                func=statsFunc[stat],
                dim="sim"
            ).expand_dims(
                {"stat": [stat]},
            )
            mList.append(s_da)

        tList.append(
            xr.concat(
                mList,
                dim="stat"
            ).expand_dims(
                {"month": [month]},
            )
        )

    processed.append(
        xr.concat(
            tList,
            dim="month"
        )
    )

data = xr.concat(
    processed,
    dim="dataType"
)


###############################################################
#
#   Plotting function
#

statsLongName: dict[ str, str ] = {
    "mean":"mean", "std":"standard deviation",
    "skew":"skewness", "kurt":"kurtosis",
}

def plotting(
        arr: xr.DataArray
) -> None:
    """
    Plot the mean, standard deviation, skewness and kurtosis of both the forecast and hindcast to comparison.
    """

    # The function has to both of the averaging protocols (mean over 2 and 3 days)
    for avg in [2, 3]:
        for s in arr.stat.values:

            plt.figure(figsize=(12,6))
            for coord in ['forecast', 'hindcast']:
                plt.plot(arr.sel(
                    dataType=coord,
                    stat=s,
                    avg=avg,
                ),
                label=coord,)

            plt.xticks(ticks=list(range(len(months))), labels=months, rotation=45)
            plt.ylabel("Total precipitation")

            plt.title(str(avg) + " days average maximums : " + statsLongName[s])
            plt.legend()
            plt.savefig(
                '/nird/projects/NS9873K/emile/unseen-storm-forecasts/plots/simulations_maximums/'
                'variations/HA_avg-fh_var-maxs_' + statsLongName[s] + '-mean' + str(avg) + '.png'
            )
            plt.close()

    pass


###############################################################
#
#   Running the script
#

if __name__ == '__main__':
    plotting(data)