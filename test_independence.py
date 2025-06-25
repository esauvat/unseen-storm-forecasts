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
import matplotlib.patches as patches
from matplotlib.axes import Axes
import seaborn as sns
import os

from weatherdata import spear_distrib
import independence_refs as refs



###############################################################
#
#       Functions
#


def correlation(
        data: xr.DataArray,
) -> tuple[xr.DataArray, list] :
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
    CI = []

    for mId in np.sort(np.unique(data.month.values)):
        month = months[mId-5]
        mArrs: list = []
        mData = data.sel(date = data.month==mId)
        CI.append(list(refs.run_CI(10000, mData[...,0].shape)))
        for lt in data.time.values:
            c = xr.apply_ufunc(
                spear_distrib,
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
    ), CI


def plot_correlations(
        data: xr.DataArray,
        CI: list,
        outputDir: str = 'results',
        show = False
) -> None:
    """
    Plot the correlation distributions for each lead time.

    :param data: Input data with dimensions "ltime", "corrs".
    :param CI: confidence intervals for reference.
    :param outputDir: Output directory to save the figure.
    """

    for mid, month in enumerate(data.month.values):
        mData = data.sel(month=month)

        # Convert to DataFrame
        df: pd.DataFrame = mData.to_dataframe(name="corr").reset_index()

        # Sort by lead time to ensure consistency
        df = df.sort_values("lead_time")

        # Split lead times
        unique_lt = sorted(df[ "lead_time" ].unique())
        n = len(unique_lt)
        sep = n//2
        lt_group1 = unique_lt[ :sep ]
        lt_group2 = unique_lt[ sep: ]

        # Create figure and axes
        fig, axes = plt.subplots(2, 1, figsize=(20, 15))
        fig.suptitle(f'Correlation distributions for {month}', fontsize=30)
        
        # Add confidence intervals
        for ci in CI[mid]:
            low, high = ci
            left, right = -0.5, sep-0.5
            rect = patches.Rectangle(
                xy=(left, low),
                width=(right-left),
                height=(high-low),
                alpha=0.4,
                color='gray'
            )
            axes[0].add_patch(rect)
        for ci in CI[mid]:
            low, high = ci
            left, right = -0.5, n-sep-0.5
            rect = patches.Rectangle(
                xy=(left, low),
                width=(right-left),
                height=(high-low),
                alpha=0.4,
                color='gray'
            )
            axes[1].add_patch(rect)
            
        
        # First half
        sns.boxplot(
            data=df[ df[ "lead_time" ].isin(lt_group1) ],
            x="lead_time", y="corr",
            ax=axes[ 0 ], fill=False, color='black',
            width = 0.5
            # box_width=6, whis_width=2
        )
        axes[ 0 ].grid(linestyle='--', color='gray', alpha=0.5)
        axes[ 0 ].set_xlabel("")
        axes[ 0 ].set_ylabel("Correlation", fontsize=15)

        # Second half
        sns.boxplot(
            data=df[ df[ "lead_time" ].isin(lt_group2) ],
            x="lead_time", y="corr",
            ax=axes[ 1 ], fill=False, color='black',
            width = 0.5
            # box_width=6, whis_width=2
        )
        axes[ 1 ].grid(linestyle='--', color='gray', alpha=0.5)
        axes[ 1 ].set_xlabel("Lead Time", fontsize=15)
        axes[ 1 ].set_ylabel("Correlation", fontsize=15)

        # Save figure
        plt.tight_layout()
        fig.savefig(os.path.join(outputDir, f'independance-{month}.png'))
        if show:
            plt.show()
        plt.close(fig)  # free memory

    pass


###############################################################
#
#       Running script
#

if __name__ == "__main__":
    da = xr.open_dataarray('data/processed-full.nc')

    corr, interv = correlation(da)
    plot_correlations(
        corr,
        interv
    )
    