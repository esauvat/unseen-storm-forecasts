   
""" This is an annex for the weatherdata module """

from weatherdata_generic import *
import numpy as np, xarray as xr


class composite_dataset :



    def __init__(self, pathListToData:str, **kwargs):
        
        onlyDirectory = kwargs.get('onlyDir', None)
        resolution = kwargs.get('resolution', None)
        years = np.array(kwargs.get('years', None))

        self.pathsToFiles = self.get_paths(pathListToData, onlyDirectory, resolution, years)        # Dict of (fileType,fileName) keys with pathToFile values
        self.fileList = self.pathsToFiles.keys()                                                    # List of tuple (fileType,fileName)
        self.dims = ("latitude","longitude","time")                                                 # Tuple of dataset's dimension
        
        sample = xr.open_dataarray(self.pathsToFiles[self.fileList[0]])

        self.grid = (sample['latitude'].values, sample['longitude'].values)

        self.compute = xr.Dataset(
            coords=dict(
                latitude = self.grid[0],
                longitude = self.grid[1],
                time = pd.date_range(start='1941-01-01', end='2024-12-31').to_numpy()
            )
        )
        
        pass



    def get_paths(self, pathListToData, onlyDirectory, resolution, years):

        pathsToFiles = {}                                                                           # Dict with self.fileList as keys and paths to files as values
        pathListToData = pathListToData.split(',')

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

        if resolution:                                                                              # Optionnal parameters
            keysToDel = []
            for key in pathsToFiles.keys():
                if not resolution in key[1]:
                    keysToDel.append(key)
            for key in keysToDel:
                del pathsToFiles[key]
        
        if len(years)!=0:
            keysToDel = []
            for key in pathsToFiles.keys():
                if not any(y in key[1] for y in years):
                    keysToDel.append(key)
            for key in keysToDel:
                del pathsToFiles[key]
        
        return pathsToFiles
    

    def open_data(self, key:tuple[str,str]) -> xr.DataArray:
        ''' Open "file" as DataArray and reshape it to fit the class attributes '''
        fileType, _ = key
        da = xr.open_dataarray(self.pathsToFiles[key])
        da = da.drop_vars(names="number", errors="ignore")
        if fileType == 'hindcast':                                                                  # Reindexing the ('hdate','time') dimension for hincast files
            da = reindex_hindcast(da)
        da = da.name = key
        return da


    def compute_time_max(self) -> None :
        ''' Compute the maximum in every files of the dataset and create a max dataset '''
        self.compute['time_max'] = (
            ('latitude','longitude'), 
            np.zeros((len(self.grid[0]),len(self.grid[1])))
        )
        max_per_file = []
        for key in self.fileList:
            data = self.open_data(self.pathsToFiles[key])
            max_per_file.append(data.max(dim='time').values)
        max_array = xr.DataArray(
            np.array(max_per_file),
            dims=("file","latitude","longitude")
        )
        self.compute['time_max'].values = max_array.max(dim='file').values