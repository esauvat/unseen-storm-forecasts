#
# This file intends to compute a 95% confidence intervalle for the
# median and interquartiles of the correlation coefficient of an 
# independent dataset
#

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import numpy as np
import xarray as xr
import pandas as pd



def experiment(
        shape: tuple[int, ...]
) :
    """Create an independant dataset and compute the median and
    interquartiles of the correlation coefficients.
    """
    
    d0, d1 = shape[0], shape[1]
    # d0 observations, d1 variables
    
    dataset = np.random.randn(
        d0, d1
    )
    C = pd.DataFrame(
        dataset
    ).corr(
        method="spearman"
    )
    C_val = C.values[np.triu_indices(d1, k=1)]
    
    med = np.median(C_val)
    [q1, q3] = np.quantile(C_val, [0.25, 0.75])
    interquartile = q3-q1
    
    bound_low = max(min(C_val), q1-1.5*(interquartile))
    bound_high = min(max(C_val), q3+1.5*(interquartile))
    
    return med, bound_low, bound_high


def run_CI(
    nb: int,
    shape: tuple[int, ...]
):
    """Compute the boundaries of the confidence intervals.

    Args:
        nb (int): Number of experiment.
        
        shape (tuple[int, int]): Shape of the datasets
    """
    
    meds = []
    bounds_low = []
    bounds_high = []
    
    for _ in range(nb):
        m, bl, bh = experiment(shape)
        meds.append(m)
        bounds_low.append(bl)
        bounds_high.append(bh)
    
    med_CI = [
        np.percentile(meds, 2.5),
        np.percentile(meds, 97.5)
    ]
    bl_CI = [
        np.percentile(bounds_low, 2.5),
        np.percentile(bounds_low, 97.5)
    ]
    bh_CI = [
        np.percentile(bounds_high, 2.5),
        np.percentile(bounds_high, 97.5)
    ]
    return med_CI, bl_CI, bh_CI