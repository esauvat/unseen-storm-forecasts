
###   
###   This is an annex for the weatherdata module
###

import os

from weatherdata import *


class composite_dataset :


    def __init__(self, pathToData:str, isDirectory:bool=False):
        self.fileList = []
        if isDirectory or pathToData.endswith('/'):
            self.fileList = [filename for filename in os.listdir(pathToData)]
        else:
            txtAsList = open(pathToData, 'r').read().split('\n')
            self.fileList = [path.split('/')[-1] for path in txtAsList]
            if self.fileList[-1] == '':
                del self.fileList[-1]
            pathToData = txtAsList[0][:-len(self.fileList[0])]   
        self.fileList = np.array(self.fileList)

        self.data = xr.concat(
            [
                xr.open_dataset(
                    os.path.join(pathToData, filename)
                ).to_dataarray(
                ).drop_vars(
                    ["number", "variable"], errors="ignore"
                ).squeeze(
                ).expand_dims(
                    dim={"filename":[filename]}
                )
                for filename in self.fileList
            ],
            dim="filename"
        )

        self.dims = xr.open_dataset(self.paths.keys[0]).to_dataarray().drop_vars("variable").dims

        pass


    def max(self, over_time:bool=False, **kwargs:np.float64) -> xr.DataArray :
        latitude = kwargs.get('latitude', None)
        longitude = kwargs.get('longitude', None)
        if latitude:
            if longitude:
                res = self.data.sel(latitude=latitude, longitude=longitude).max(dim="filename")
            else:
                res = self.data.sel(latitude=latitude).max(dim="filename")
        elif longitude:
            res = self.data.sel(longitude=longitude).max(dim="filename")
        else:
            res = self.data.max(dim="filename")
        if over_time:
            return res.max(dim="time")
        return res