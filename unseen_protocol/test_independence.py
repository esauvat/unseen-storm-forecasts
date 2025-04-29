#
# The independance test assess that the ensemble members are uncorrelated for each of the
# selected lead times
#

import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from weatherdata import spear_distrib, mean_over_time



###############################################################
#
#       Functions
#

def correlation(
        data: xr.DataArray,
) -> xr.DataArray:
    """
    Compute the correlation for each lead time.

    :param data: Input data with dimensions "idate", "number", "time"
    """

    if not all([ dim in data.dims for dim in [ "idate", "number", "time" ] ]):
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
    data = data.sel(number=numbers)

    arrays: list = [ ]

    for lt in data.time.values:
        c = xr.apply_ufunc(
            spear_distrib,
            data.sel(time=lt),
            input_core_dims=[ [ "number", "idate" ] ],
            output_core_dims=[ [ "corrs" ] ],
            vectorize=True
        )
        arrays.append(
            c.expand_dims({ "ltime":[ lt ] })
        )

    return xr.concat(
        arrays,
        dim="ltime"
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

    # Convert to DataFrame
    df: pd.DataFrame = data.to_dataframe(name="corr").reset_index()

    # Sort by lead time to ensure consistency
    df = df.sort_values("ltime")

    # Split lead times
    unique_lt = sorted(df[ "ltime" ].unique())
    lt_group1 = unique_lt[ :14 ]
    lt_group2 = unique_lt[ 14: ]

    # Create figure and axes
    fig, axes = plt.subplots(2, 1, figsize=(20, 15))
    fig.suptitle("Correlation distributions", fontsize=20)

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
    fig.savefig(os.path.join(outputDir, "independance.png"))
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
            mean_over_time(
                da, span=3, edges=False
            )
        )
    )
