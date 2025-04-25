#
# The fidelity test aims to assess the precision of the model, compared to the reanalysis data.
#
# To do so we retrieve the reanalysis data and through a bootstrapping of the modelled data to
# fit the shape of the reanalysis, we can verify if the mean, standard deviation, skewness and
# kurtoisis of the "UNSEEN" senarios fit what can be expected in real life.
#

import os

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from numpy.typing import ArrayLike, NDArray
from scipy import stats



###############################################################
#
#       Functions
#

def bootstrap_samples(
        size: int,
        ds_mod: xr.Dataset,
        month: int,
        sample_nb: int
) -> xr.DataArray:
    """
    Select random samples of mod_da elements, matching the shape of rea_da.

    :param size: size of the bootstraps samples.
    :param ds_mod: modelled data.
    :param month: working month.
    :param sample_nb: number of bootstrap samples to create.
    """

    da_samples = xr.DataArray(
        data=np.full(
            shape=(sample_nb, size),
            fill_value=np.nan
        ),
        dims=[ "bsId", "obj" ]
    )

    mask = ds_mod[ 'month' ] == month
    vals: NDArray = (
        xr.where(mask, ds_mod[ 'tp24' ], np.nan).values.flatten()
    )
    nonan_vals: NDArray = vals[ ~np.isnan(vals) ]

    assert len(nonan_vals) > size, "Not enough data to bootstrap sample"
    rng = np.random.default_rng()
    for idx in range(sample_nb):
        da_samples[ idx, : ] = rng.choice(
            nonan_vals, size=size,
            replace=False, shuffle=False
        )

    return da_samples


def main(
        modPath: str = 'data/processed-full.nc',
        reaPath: str = 'data/processed-rea.nc'
) -> tuple[ NDArray, NDArray ]:
    """
    Compute the  statistical attributes from a bootstrapped sampling
    of the modelled data to the shape of the reanalysis one.

    :return: NDArrays of the mean, std, skewness and kurtoisis of the
        observed data and the boostrapped simulated data.
    """

    modelled = xr.open_dataset(modPath)
    reanalysis = xr.open_dataarray(reaPath)

    bsSize = len(reanalysis.values)
    bsNb = 10000
    distribsAttrs = np.zeros((6, 4, bsNb))
    statFuncList = [ np.mean, np.std, stats.skew, stats.kurtosis ]
    for mIdx, month in enumerate(list(range(5, 11))):
        samples = bootstrap_samples(
            bsSize, modelled, month, bsNb
        )
        for sIdy in range(4):
            distribsAttrs[ mIdx, sIdy, : ] = samples.reduce(
                func=statFuncList[ sIdy ],
                dim="obj"
            )

    reaAttrs = xr.concat(
        [
            reanalysis.reduce(func, dim="year")
            for func in statFuncList
        ],
        dim="new_dim"
    ).transpose("month", "new_dim").values

    return reaAttrs, distribsAttrs


def plot(
        reaAttrs: ArrayLike,
        modAttrs: ArrayLike,
        save_dir: str = 'results'
) -> None:
    """
    Plot the distribution of the bootstrapped distribution attributes.

    :param reaAttrs: Attributes of the reanalysis distribution for each month
        of the May-October period. The shape must be (6, 4).
    :param modAttrs: Attributes of the bootstrapped modelled data for each month
        and each bootstrap sample. The shape must be (6, 4, bsNb).
    :param save_dir: Directory to save the plots.
    """

    months = [ 'May', 'June', 'July', 'August', 'September', 'October' ]
    attrsLongName = [ "Mean", "Standard deviation", "Skewness", "Kurtosis" ]

    for mId, month in enumerate(months):
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'Fidelity test for {month}', fontsize=16)

        for sId, splot in enumerate(axs.flatten()):
            simulated = modAttrs[ mId, sId, : ]
            observed = reaAttrs[ mId, sId ]

            # Histogram of simulated data
            splot.hist(simulated, bins=30, alpha=0.7, density=True, color='skyblue', edgecolor='black')
            splot.axvline(observed, color='red', linestyle='-', linewidth=2, label='Observed')

            # 95% confidence interval
            lower = np.percentile(simulated, 2.5)
            upper = np.percentile(simulated, 97.5)
            splot.axvline(lower, color='black', linestyle='dotted', linewidth=1.5, label='95% CI')
            splot.axvline(upper, color='black', linestyle='dotted', linewidth=1.5)

            splot.set_title(attrsLongName[ sId ])
            splot.legend()

        save_path = os.path.join(save_dir, f"fidelity-{month}.png")
        plt.savefig(save_path)
        plt.close(fig)  # Close to free memory


###############################################################
#
#       Running script
#
import time

if __name__ == "__main__":
    rea, mod = main()
    plot(rea, mod)
