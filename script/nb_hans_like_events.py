#
# Script to plot, for each month, the number of simulated events that exceed a certain threshold, which will be
# set using the data of Hans, after applying a percentage.
#
# Prerequisites : the file "worst_event_simulation.py" must have been already run, since we'll use its results,
# which are stored on the two netCDF files :
#   - 'weathersets/results/s2s-HA_avg-all_res-worst_event_simulated-mean2.nc'
#   - 'weathersets/results/s2s-HA_avg-all_res-worst_event_simulated-mean3.nc'
#
# NB : the paths to these files can be found in the "compute" attribute of the Weatherset object, using the files name
# as keys.
#

###################################################################################################
#
#       Packages
#

import pickle

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from weatherdata.classes import Weatherset



###################################################################################################
#
#       Functions
#

def get_nb_of_events(
        data: xr.DataArray,
        threshold: float
) -> list[ int ]:
    """ Return the list of event amount that exceed the threshold value for each month """

    exceedingData = data.where(data > threshold, drop=True)
    res = [ 0 for _ in range(12) ]

    for idx in range(len(exceedingData.values)):
        month = exceedingData[ 'olMonth' ].values[ idx ] - 1
        res[ month ] += 1

    return res


def main(
        tpSet: Weatherset,
        data: str,
        percentValues: np.ndarray[ tuple[ int, ], float ],
) -> None:
    """ Plot the number of events that exceed different values linked to hans for every month """

    treatmentType = data.split('-').pop()
    with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/'
              'weathersets/continuous_0.5.pkl', 'rb') as era5:
        hansValue: str = xr.open_dataarray(
            pickle.load(era5).compute[
                "continuous_hans-area-avg-" + treatmentType + "_0.5_monthly-max"
                ]
        ).sel(years='2023', months='aug').values

    arr = xr.open_dataarray(
        tpSet.compute[ data ]
    )

    thesholdValues = percentValues * hansValue
    months = [
        'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
    ]

    plt.figure(figsize=(12, 6))

    for idx, threshold in enumerate(thesholdValues):
        percentage = str(
            int((percentValues[ idx ] * 100) // 1)
        ) + "%"
        plt.plot(get_nb_of_events(arr, threshold), label=percentage + " of Hans")

    plt.legend()
    plt.xticks(ticks=list(range(12)), labels=months, rotation=45)
    plt.title(
        "Number of simulated events exceeding fractions of Hans"
    )

    plt.savefig(
        '/nird/projects/NS9873K/emile/unseen-storm-forecasts/plots/simulations_maximums/'
        'hans_exceeding_numbers-' + treatmentType + '.png'
    )

    pass


###################################################################################################
#
#       Running the script
#

defaultPercents = np.arange(0.85, 1.05, 0.05)
defaultFile = "s2s-HA_avg-all_res-worst_event_simulated-mean2"

if __name__ == "__main__":

    import sys



    args = sys.argv
    if len(args) <= 1:
        dataFile = defaultFile
        percents = defaultPercents
    elif len(args) == 2:
        dataFile = args[ 1 ]
        percents = defaultPercents
    else:
        dataFile = args[ 1 ]
        percents = args[ 2: ]

    with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/'
              'weathersets/s2s_all-res.pkl', 'rb') as inp:
        set = pickle.load(inp)

    globals()[ "main" ](
        tpSet=set,
        data=dataFile,
        percentValues=percents,
    )
