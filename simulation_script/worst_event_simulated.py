#
#   Script to compute the worst event for each simulation :
#       For each netcdf file we take every simulation, ensemble members and hindcast
#       dates, and we search for the heaviest precipitations.
#
#       We consider the lead times 15 to 45, given that 15 is the minimum required amount
#       of time for the ensemble members to be independent (see results from correlation.py
#       and ensemble_members_std.py)
#
#       The results will be plotted twice :
#           - One time by binning the obtained value on the month that overlap the most
#           the time range that was considered. This allows to get a monthly distribution,
#           while avoiding the underrepresentation of dryer months, which would happen if
#           we were binning the value on the month of the event's date.
#           - The other time will be by binning the value on the precise date on which the
#           simulated event happened, this will probably cause the previously mentionned
#           problem, but will give a more smooth distribution.
#
#       To ensure such plotting, the resulting array will have the following dimensions :
#
#           dimensions :    - Simulation reference (no index)
#
#           coordinates:    - initialization date (sim)
#                           - hindcast date (sim)
#                           - ensemble member (sim)
#                           - time (sim)
#                           - overlap month (sim)
#

###################################################################################################
#
#   Packages
#

import numpy as np
import xarray as xr

import weatherdata as wd
from weatherdata.geographics import apply_curv_weights
from weatherdata.classes import Weatherset



###################################################################################################
#
#   Variables definition
#

# Hans' areas boundValues
lats: slice(float, float) = (
    slice(62.75, 60.5))
longs: slice(float, float) = (
    slice(9, 11.75))

# Dictionary to convert treatment type into time span
typeDict: dict[ str:int ] = {
    "daily":None, "mean2":2, "mean3":3 }

# Minimum lead time for uncorrelated ensemble members
firstUncorrelated: int = 16


###################################################################################################
#
#   Auxiliary functions
#

def open_files(
        initializationDate: str,
        tpSet: Weatherset,
) -> xr.DataArray:
    """ Open all files starting on the initialization date and concatenate them """

    # The initialization date is a string refering to at least one file. The files name contain the resolution and
    # the date. An example would be (for 0.5˚ resolution and 08/06/2003 date) :
    #   eg : tp24_0.5x0.5_2003-06-08.nc
    # They can be accessed quicker and with a more standardized structure using open_data function in the
    # Weatherset class, which take for arguments a key tuple (type, name) where type is amongst forecast and hindacst
    #   eg : ('forecast', 'tp24_0.5x0.5_2003-06-08')
    # note that the name does not contain '.nc'
    #
    # The files are concatenated first by resolution if multiple ones coexist in the Weatherset
    #   Such concatenation is made on the time dimension since high resolution (0.25°) files contain the data for
    #   the 15 first days (0-14) and low resolution (0.5°) files contain the data for the last 31 days
    #
    # Then, if multiple types are present, for better agregation we consider the forecast DataArray as a hindcast
    # starting on the actual initialization date. We can then concatenate over the hdate dimension, after extending
    # the forecast with a hdate dimension, setting the coordinate as the initialization date in its int form.
    #
    #
    # Depending on the initialization date and the file type, multiple case can and will occur :
    #
    #   - for low resolution files created after 2024-06-29, the amount of ensemble members goes from 51 to 101
    #   and the time series goes from 1 to 45, given that we work on the averaged precipitations over Hans area,
    #   for later dates only low resolution files will be used, given that they provide the same information as
    #   higher resolution ones.
    #
    #   - after 2022-12-29 for low resolution and 2023-08-27 for high resolution, only forecast files exist
    #
    #   - in the hincast files, the number coordinates are as follows :
    #       number == xr.DataArray(
    #           values = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 51])
    #           dims = ("number")
    #       )
    #   this specificity is not treated in this function but will need to be adressed along the diferent amount of
    #   ensemble members one late to save memory space by not storing arrays full of NaN.

    #############################################
    #   Create the keys list
    #
    #   The list is determined using the following oracle :
    #
    #   type        | date>22-12-29 | date>23-06-29 | firstUnco>=15 | keys
    # --------------|---------------|---------------|---------------|--------------------------------
    #   multi       | True          | True          | True          | [forecast] x [lowres]
    #   multi       | True          | True          | False         | [forecast] x [lowres]
    #   multi       | True          | False         | True          | [forecast] x [lowres]
    #   multi       | True          | False         | False         | [forecast] x [lowres, highres]
    #   multi       | False         | False         | True          | [forecast, hindcast] x [lowres]
    #   multi       | False         | False         | False         | [forecast, hindcast] x [lowres, highres]
    #   forecast    | True          | True          | True          | [forecast] x [lowres]
    #   forecast    | True          | True          | False         | [forecast] x [lowres]
    #   forecast    | True          | False         | True          | [forecast] x [lowres]
    #   forecast    | True          | False         | False         | [forecast] x [lowres, highres]
    #   forecast    | False         | False         | True          | [forecast] x [lowres]
    #   forecast    | False         | False         | False         | [forecast] x [lowres, highres]
    #   hindcast    | True          | True          | True          | pass
    #   hindcast    | True          | True          | False         | pass
    #   hindcast    | True          | False         | True          | pass
    #   hindcast    | True          | False         | False         | pass
    #   hindcast    | False         | False         | True          | [hindcast] x [lowres]
    #   hindcast    | False         | False         | False         | [hindcast] x [lowres, highres]
    #
    #   Which is simplified into :
    #
    #   type        | date>22-12-29 | typeList
    # --------------|---------------|----------------------
    #   multi       | True          | [forecast]
    #   multi       | False         | [forecast, hindcast]
    #   forecast    | Any           | [forecast]
    #   hindcast    | True          | pass
    #   hindcast    | False         | [hindcast]
    #
    #   and if not pass
    #
    #   date>23-06-29   | firstUnco>=15 | nameList
    # ------------------|---------------|------------------
    #   True            | True          | [lowres]
    #   True            | False         | [lowres]
    #   False           | True          | [lowres]
    #   False           | False         | [lowres, highres]

    if tpSet.multiType and initializationDate > '2022-12-29':
        typeList = [
            'forecast'
        ]
    elif tpSet.multiType:
        typeList = [
            'forecast', 'hindcast'
        ]
    else:
        setType: str = tpSet.fileList[ 0 ][ 0 ]
        if setType == 'forecast':
            typeList = [
                'forecast'
            ]
        elif initializationDate <= '2022-12-29':
            typeList = [
                'hindcast'
            ]
        else:
            return None

    if initializationDate > '2023-06-29' or firstUncorrelated >= 15:
        nameList = [
            'tp24_0.5x0.5_' + initializationDate
        ]
    else:
        nameList = [
            'tp24_0.5x0.5_' + initializationDate,
            'tp24_0.25x0.25_' + initializationDate
        ]

    #############################################
    #   Open and concatenate files

    arrays: list[ xr.DataArray ] = [ ]
    for fileType in typeList:
        sameTypeArrays: list[ xr.DataArray ] = [ ]
        for fileName in nameList:
            arr = tpSet.open_data(
                key=(fileType, fileName)
            ).sel(latitude=lats, longitude=longs)

            sameTypeArrays.append(
                apply_curv_weights(arr).mean(
                    dim=[ "latitude", "longitude" ]
                )
            )
        res = xr.concat(
            sameTypeArrays,
            dim="time"
        ).expand_dims(
            dict(fdate=np.array([ initializationDate ]))
        )

        if "hdate" in res.dims:
            arrays.append(
                res.stack(sim=[ "fdate", "hdate", "number" ])
            )
        else:
            arrays.append(
                res.stack(sim=[ "fdate", "number" ])
            )

    #############################################
    #   Select only high enough lead time

    res = xr.concat(
        arrays,
        dim="sim"
    )

    firstCurrentUnco = (
            np.datetime64(initializationDate)
            + np.timedelta64(firstUncorrelated, 'D'))
    res = res.sel(
        time=(res.coords[ 'time' ] >= firstCurrentUnco)
    )

    return res


def determine_overlap_month(
        firstDate: np.datetime64,
        lastDate: np.datetime64
) -> int:
    """ Determine which month overlap the most with the time extent given by firstDate
    and lastDate and return its number """

    # First check if a full month exists between the dates
    firstMonth: int = firstDate.astype(object).month
    lastMonth: int = lastDate.astype(object).month
    firstMonthNumber: int = firstDate.astype('datetime64[M]').astype(int)
    lastMonthNumber: int = lastDate.astype('datetime64[M]').astype(int)
    if (lastMonthNumber - firstMonthNumber) == 2:
        return (firstMonth + 1) % 12
    else:
        # Determine the lenght of the extent:
        lenght: int = wd.date_as_int(lastDate) - wd.date_as_int(firstDate)
        lastDayNumber = lastDate.astype(object).day
        if lastDayNumber >= (lenght // 2):
            return lastMonth
        else:
            return firstMonth


###################################################################################################
#
#   Main function
#

def main(
        tpSet: Weatherset,
        treatmentType: str | None = "daily",
):
    """ Compute the worst event for each simulation """

    # For each initialization date, we use open_files to obtain the concatenated array of all
    # the values linked to this initialization date. We then need to determine the worst event.
    #
    # The second part will be to reshape the array to delete all possible empty parts (full of
    # Nan) in the array to gain place

    # List of all the initialization dates, nb : init dates are drawn from only low resolution files because fewer exist but
    # low resolution is always necessary
    lResArr = np.array(tpSet.fileList)[
        np.where(np.array(
            [ fileName[ 5:-11 ] for _, fileName in tpSet.fileList ]
        ) == '0.5x0.5')
    ]
    initDateList: np.ndarray[ tuple[ int, ], str ] = np.unique([ fileName[ -10: ] for _, fileName in lResArr ])
    # Temporary storage for results arrays before concatenation
    resultsList: list[ xr.DataArray ] = [ ]
    # Time span for possible averaging in time
    span: int = typeDict[ treatmentType ]

    #############################################
    #   Process each file
    for date in initDateList:
        data = open_files(date, tpSet)
        # data : xr.DataArray(
        #   values = np.array("""avg tp over hans area""")
        #   dims = (time,
        #           sim=MultiIndex(fdate,hdate,number) ) )
        if span:
            data = wd.mean_over_time(
                data, span, edges=False
            )

        # Select each required information:
        valMax = data.max(dim="time")
        dateMax = data.idxmax(dim="time")
        olMonth = np.full(
            valMax.values.shape,
            determine_overlap_month(
                np.datetime64(date) + np.timedelta64(firstUncorrelated, 'D'),
                np.datetime64(date) + np.timedelta64(45, 'D')
            )
        )
        valMax = valMax.assign_coords(
            {
                "time":("sim", dateMax.values),
                "olMonth":("sim", olMonth) }
        )

        resultsList.append(valMax)

    del valMax, dateMax, olMonth, data

    #############################################
    #   Create the resulting array

    res = xr.concat(
        resultsList,
        dim="sim"
    )
    del resultsList  # Delete the results list to free space

    name = "s2s-HA_avg-all_res-worst_event_simulated-" + treatmentType
    path = set.results + name + ".nc"

    # Remove MultiIndexes
    res = res.reset_index("sim")

    res.to_netcdf(path)
    tpSet.compute[ name ] = path

    return res
    ### END ###


###################################################################################################
#
#   Run section
#

wsPath = '/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_all-res.pkl'

import pickle



with open(wsPath, 'rb') as inp:
    set: Weatherset = pickle.load(inp)

mean2Maxs = main(set, "mean2")
mean3Maxs = main(set, "mean3")

with open(wsPath, 'wb') as outp:
    pickle.dump(set, outp, pickle.HIGHEST_PROTOCOL)

#   Create the plots

import matplotlib.pyplot as plt
import seaborn as sns



def plot_monthly(
        arr: xr.DataArray,
        title: str,
        treatmentType: str | None = "daily"
) -> None:
    months = np.arange(1, 13)
    monthsLabels = [
        'jan', 'feb', 'mar', 'apr', 'may', 'jun',
        'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
    ]
    vals = [
        arr.where(arr[ 'olMonth' ] == m, drop=True).values for m in months
    ]

    plt.figure(figsize=(12, 6))
    sns.boxplot(data=vals)

    # Determining Hans value for reference
    monthlyMaxERA5 = xr.open_dataarray(
        '/nird/projects/NS9873K/emile/unseen-storm-forecasts/'
        'weathersets/results/continuous_hans-area-avg-' + treatmentType + '_0.5_monthly-max.nc',
    )
    hansValue = monthlyMaxERA5.sel(
        years='2023', months='aug'
    )
    plt.plot([hansValue for _ in range(len(months))], color='red')
    plt.text(0, 1.01*hansValue, "Hans", color='red')

    plt.xticks(ticks=list(range(12)), labels=monthsLabels, rotation=45)
    plt.ylabel('total precipitation (m)')
    plt.title(title)
    path = ('/nird/projects/NS9873K/emile/unseen-storm-forecasts/plots/simulations_maximums/HA_avg-months-maxs_'
    + treatmentType + '.png')
    plt.savefig(path)

    pass


# def plot_daily(
#         arr: xr.DataArray,
#         title: str,
#         path: str
# ) -> None:
#     def get_cal_idx(
#             da: xr.DataArray
#     ) -> xr.DataArray:
#         val = np.array([
#             100 * date.month + date.day for date in
#             da.values.astype('datetime64[D]').astype(object)
#         ])
#         res = xr.full_like(da, np.nan)
#         res.values = val
#         return res
#
#     days = np.arange(
#         np.datetime64('2000-01-01'),
#         np.datetime64('2001-01-01'),
#         np.timedelta64(1, 'D')
#     )
#     vals = [
#         arr.where(get_cal_idx(arr[ 'time' ]) == dateIdx, drop=True)
#         for dateIdx in get_cal_idx(xr.DataArray(days)).values
#     ]
#
#     plt.figure(figsize=(12, 6))
#     sns.boxplot(data=vals)
#
#     plt.xticks(ticks=list(range(366)))
#     plt.ylabel('total precipitation (m)')
#     plt.title(title)
#     plt.savefig(path)
#
#     pass


plot_monthly(
    mean2Maxs, "2 days average maximums for each simulation",
    "mean2"
)
plot_monthly(
    mean3Maxs, "3 days average maximums for each simulation",
    "mean3"
)

# plot_daily(
#     mean2Maxs, "2 days average maximums for each simulation",
#     '/nird/projects/NS9873K/emile/unseen-storm-forecasts/plots/simulations_maximums/HA_avg-days-maxs_mean2.png'
# )
# plot_daily(
#     mean3Maxs, "3 days average maximums for each simulation",
#     '/nird/projects/NS9873K/emile/unseen-storm-forecasts/plots/simulations_maximums/HA_avg-days-maxs_mean3.png'
# )
