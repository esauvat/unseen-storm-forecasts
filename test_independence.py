#
# The independance test assess that the ensemble members are uncorrelated for each of the
# selected lead times
#

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"

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


def correlation(
        data: xr.DataArray,
) -> xr.DataArray:
    """
    Compute the correlation for each lead time.

    :param data: Input data with dimensions "date", "number" and "time". The "time" dimension store
        the lead time information.
    """

    if not all([ dim in data.dims for dim in [ "time", "number", "date" ] ]):
        raise ValueError("Input DataArray must have dimensions: 'date', 'number', 'time'.")

    # Select the ensemble members that are shared between all files
    if data.date.min().values < np.datetime64('2019') :
        numbers = xr.DataArray(
            np.array(
                [ i for i in range(1, 11) ] + [ 51 ]
            ),
            dims="number"
        )
    else:
        numbers = data.number
    data = data.sel(number=numbers)

    arrays: list = [ ]
    months = ["May", "June", "July", "August", "September", "October"]

    for mId, month in enumerate(months):
        mArrs: list = []
        mData = data.where(data.month == mId+5, drop=True)
        for lt in data.time.values:
            c = xr.apply_ufunc(
                pears_distrib,
                mData.sel(time=lt),
                input_core_dims=[ [ "number", "date" ] ],
                output_core_dims=[ [ "corrs" ] ],
                vectorize=True
            )
            mArrs.append(
                c.expand_dims({ "lead_time":[ lt ] })
            )
        arrays.append(
            xr.concat(
                mArrs,
                dim="lead_time"
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
        df = df.sort_values("lead_time")

        # Split lead times
        unique_lt = sorted(df[ "lead_time" ].unique())
        lt_group1 = unique_lt[ :14 ]
        lt_group2 = unique_lt[ 14: ]

        # Create figure and axes
        fig, axes = plt.subplots(2, 1, figsize=(20, 15))
        fig.suptitle(f'Correlation distributions for {month}', fontsize=20)

        # First half
        sns.violinplot(
            data=df[ df[ "lead_time" ].isin(lt_group1) ],
            x="lead_time", y="corr",
            ax=axes[ 0 ], fill=False, color='black',
            inner_kws=dict(box_width=6, whis_width=2)
        )
        axes[ 0 ].grid(linestyle='--', color='gray', alpha=0.5)
        axes[ 0 ].set_xlabel("Lead Time")
        axes[ 0 ].set_ylabel("Correlation")

        # Second half
        sns.violinplot(
            data=df[ df[ "lead_time" ].isin(lt_group2) ],
            x="lead_time", y="corr",
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
    da = xr.open_dataarray('data/processed-full.nc')

    plot_correlations(
        correlation(
            da
        )
    )
    