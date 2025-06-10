#
# Apply a bias correction to the data, in order to assess the fidelity test
#
# We correct every month to get in the exact center of the mean distribution
# in order to keep the same treatment between all months, some having a strong bias 
# and other a bias small enough so that the observed mean falls just on the edge
# of the 95% CI.
#

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import numpy as np
import xarray as xr



data = xr.open_dataarray(
    "second_correction/v1/corrected_1.nc"
)

# The corrections are as follows :
#   → May : mean+=4.6
#   → June : mean+=4.2
#   → July : mean+=2.1
#   → August : 