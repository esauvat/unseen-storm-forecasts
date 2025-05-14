#
# The independance test assess that the ensemble members are uncorrelated for each of the
# selected lead times
#

from numpy.typing import NDArray

import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from weatherdata import pears_distrib, sum_over_time



###############################################################
#
#       Functions
#

def preprocess(
        data: xr.DataArray,
) -> xr.DataArray:
    """
    Flatten the DataArray, keeping only a leadtime and time coordinates.
    """

    data = data.stack(obj=["idate", "time"]).rename(
        {"time":"lead_time"}
    )
    hdate_to_dt = (
        lambda d : np.datetime64(
                "-".join([str(d)[:4], str(d)[4:6], str(d)[6:]])
            )
        )

    timeShifts: NDArray = np.array(
            [np.timedelta64(d, 'D')
            for d in np.unique(data.lead_time.values)]
        ).flatten()

    idateRepeatAdd = xr.DataArray(
        np.zeros(len(np.unique(data.hdate.values))),
        coords = [("hdate", np.unique(data.hdate.values))]
    )

    newTimes: list = []

    idateIdx = np.unique(
        pd.MultiIndex.from_arrays(
            [data.hdate.values, data.fdate.values]
        )
    )
    for (hd, _) in idateIdx:
        addon = int(idateRepeatAdd.sel(hdate=hd).values)
        idateRepeatAdd.loc[hd] = addon + 1
        newTimes.append(
            hdate_to_dt(hd) + np.timedelta64(addon, 's') + timeShifts
        )

    newTimes = np.array(newTimes).flatten()

    return data.reset_index("obj").drop_vars(
        ["idate", "fdate"]
    ).rename(
        { "obj":"time" }
    ).assign_coords(
        time=newTimes
    )


def correlation(
        data: xr.DataArray,
) -> xr.DataArray:
    """
    Compute the correlation for each lead time.

    :param data: Input data with dimensions "number", "time"
    """

    if not all([ dim in data.dims for dim in [ "number", "time" ] ]):
        raise ValueError("Input DataArray must have dimensions: 'month', 'ltime', 'obj'.")

    # Select the ensemble members that are shared between all files
    if data.hdate.min().values < 20200000:
        numbers = xr.DataArray(
            np.array(
                [ i for i in range(1, 11) ] + [ 51 ]
            ),
            dims="number"
        )
    else:
        numbers = data.number
    data = data.sel(number=numbers).where(data.lead_time<44, drop=True)

    arrays: list = [ ]
    months = ["May", "June", "July", "August", "September", "October"]

    for mId, month in enumerate(months):
        mArrs: list = []
        mData = data.where(data.time['time.month'] == mId+5, drop=True)
        for lt in data.time.values:
            c = xr.apply_ufunc(
                pears_distrib,
                mData.where(mData.lead_time==lt, drop=True),
                input_core_dims=[ [ "number", "time" ] ],
                output_core_dims=[ [ "corrs" ] ],
                vectorize=True
            )
            mArrs.append(
                c.expand_dims({ "ltime":[ lt ] })
            )
        arrays.append(
            xr.concat(
                mArrs,
                dim="ltime"
            ).expand_dims(
                {"month":[month]}
            )
        )

    return xr.concat(
        arrays,
        dim="month"
    )


def plot_correlations(
        data: xr.DataArray,
        outputDir: str = 'results'
) -> None:
    """
    Plot the correlation distributions for each lead time.

    :param data: Input data with dimensions "ltime", "corrs".
    :param outputDir: Output directory to save the figure.
    """

    for month in data.month.values:
        mData = data.sel(month=month)

        # Convert to DataFrame
        df: pd.DataFrame = mData.to_dataframe(name="corr").reset_index()

        # Sort by lead time to ensure consistency
        df = df.sort_values("ltime")

        # Split lead times
        unique_lt = sorted(df[ "ltime" ].unique())
        lt_group1 = unique_lt[ :14 ]
        lt_group2 = unique_lt[ 14: ]

        # Create figure and axes
        fig, axes = plt.subplots(2, 1, figsize=(20, 15))
        fig.suptitle(f'Correlation distributions for {month}', fontsize=20)

        # First half
        sns.violinplot(
            data=df[ df[ "ltime" ].isin(lt_group1) ],
            x="ltime", y="corr",
            ax=axes[ 0 ], fill=False, color='black',
            inner_kws=dict(box_width=6, whis_width=2)
        )
        axes[ 0 ].grid(linestyle='--', color='gray', alpha=0.5)
        axes[ 0 ].set_xlabel("Lead Time")
        axes[ 0 ].set_ylabel("Correlation")

        # Second half
        sns.violinplot(
            data=df[ df[ "ltime" ].isin(lt_group2) ],
            x="ltime", y="corr",
            ax=axes[ 1 ], fill=False, color='black',
            inner_kws=dict(box_width=6, whis_width=2)
        )
        axes[ 1 ].grid(linestyle='--', color='gray', alpha=0.5)
        axes[ 1 ].set_xlabel("Lead Time")
        axes[ 1 ].set_ylabel("Correlation")

        # Save figure
        fig.savefig(os.path.join(outputDir, f'independance-{month}.png'))
        plt.close(fig)  # free memory

    pass


###############################################################
#
#       Running script
#

if __name__ == "__main__":
    da = xr.open_dataarray('data/retrieved-full.nc')

    plot_correlations(
        correlation(
            preprocess(
                sum_over_time(
                    da, span=3, edges=False
                )
            )
        )
    )
