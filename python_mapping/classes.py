
###   
###   This is an annex for the weatherdata module
###

from weatherdata import *
import numpy as np, xarray as xr


class composite_dataset :


    def __init__(self, pathListToData:str, **kwargs):
        
        onlyDirectory = kwargs.get('onlyDir', None)
        resolution = kwargs.get('resolution', None)
        years = np.array(kwargs.get('years', None))

            # Dict of (fileType,fileName) keys with pathToFile values
        pathsToFiles = self.get_paths(pathListToData, onlyDirectory, resolution, years)
            # List of tuple (fileType,fileName)
        self.fileList = pathsToFiles.keys()

        datasets = []
        for (fileType,fileName) in self.fileList:
            ds = xr.open_dataset(pathsToFiles[(fileType,fileName)])
            ds = ds.drop_vars("number", errors="ignore")
            ds = ds.squeeze()
            if fileType == 'hindcast':
                da = ds.to_dataarray()
                ds = reindex_hindcasts(da)
            ds = ds.expand_dims(dim={"fileType":[fileType], "fileName":[fileName]})
            ds = ds.stack(reference = ("fileType", "fileName"))
            datasets.append(ds)

        self.data = xr.concat(datasets, dim="reference")

        self.dims = ds.to_dataarray().squeeze("variable").dims
        
        pass



    def get_paths(self, pathListToData, onlyDirectory, resolution, years):

        pathsToFiles = {}       # Dict with self.fileList as keys and paths to files as values

        if onlyDirectory:
            for dir in pathListToData:
                extract_files(dir, pathsToFiles)
        else:
            for loc in pathListToData:
                if loc.endswith('/'):
                    extract_files(loc, pathsToFiles)
                else:
                    txtAsList = open(loc, 'r').read().split('\n')
                    if txtAsList[-1] == '':
                        del txtAsList[-1]
                    for fileLoc in txtAsList:
                        fileLocScatter = fileLoc.split('/')
                        filename = fileLocScatter.pop()
                        type = ''
                        while fileLocScatter != []:
                            dir = fileLocScatter.pop()
                            if dir == 'daily':
                                type = fileLocScatter[-1]
                                break
                        assert type != '', "Wrong file path in the document"
                        pathsToFiles[(type, filename[:-3])] = fileLoc
        
        # Optionnal parameters

        if resolution:
            for key in pathsToFiles.keys():
                if not resolution in key[1]:
                    del pathListToData[key]
        
        if years:
            for key in pathsToFiles.keys():
                if not any(y in key[1] for y in years):
                    del pathListToData[key]
        
        return pathsToFiles


    def max(self, *args:str, **kwargs:np.float64) -> xr.DataArray :
        latitude = kwargs.get('latitude_sel', None)
        longitude = kwargs.get('longitude_sel', None)
        time = kwargs.get('time_sel', None)

        res = self.data

        if latitude & longitude:
            res = res.sel(latitude=latitude, longitude=longitude).max(dim="reference")
        elif latitude:
            res = res.sel(latitude=latitude).max(dim="reference")
        elif longitude:
            res = res.sel(longitude=longitude).max(dim="reference")

        if time:
            res = res.sel(time=time)
        
        return res.max(dim=["reference"]+list(args))