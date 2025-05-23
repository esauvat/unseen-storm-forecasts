#
# Apply the first correction to the unseen protocol.
# It will correct the data by adjusting the mean of the
# modelled distributions to the mean of the observed distribution.
#

from sys import argv
import xarray as xr



#
#       Script
#

if __name__ == "__main__":

    if len(argv) >= 2 and argv[1] == "forecast":
        selector = "forecast"
    elif len(argv) >= 2 and argv[1] == "hindcast":
        selector = "hindcast"
    else:
        selector = "full"

    data = xr.open_dataset("data/processed-"+selector+".nc")

    data['tp24'].values = data['tp24'].values + 7
    data.to_netcdf("data/uni_corrected-"+selector+".nc")