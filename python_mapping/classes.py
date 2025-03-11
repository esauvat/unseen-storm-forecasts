   
""" This is an annex for the weatherdata module """

from weatherdata_generic import *
import numpy as np, xarray as xr


class composite_dataset :



    def __init__(self, pathListToData:list[str], **kwargs):
        
        onlyDirectory = kwargs.get('onlyDir', None)
        resolution = kwargs.get('resolution', None)
        years = np.array(kwargs.get('years', []))

        self.pathsToFiles = self.get_paths(pathListToData, onlyDirectory, resolution, years)        # Dict of (fileType,fileName) keys with pathToFile values
        self.fileList = [key for key in self.pathsToFiles.keys()]                                   # List of tuple (fileType,fileName)
        self.dims = ("latitude","longitude","time")                                                 # Tuple of dataset's dimension
        
        sample = xr.open_dataarray(self.pathsToFiles[self.fileList[0]])

        latitudeOfFirstGridPoint = sample['latitude'].values[0]
        latitudeOfLastGridPoint = sample['latitude'].values[-1]
        longitudeOfFirstGridPoint = sample['longitude'].values[0]
        longitudeOfLastGridPoint = sample['longitude'].values[-1]
        if '0.25x0.25' in self.fileList[0][1]:
            nbLat = len(sample['latitude'].values)
            nbLon = len(sample['longitude'].values)
        else:
            nbLat = 2*len(sample['latitude'].values)-1
            nbLon = 2*len(sample['longitude'].values)-1

        self.coords = xr.DataArray(
            dims = ("latitude","longitude"),
            coords = dict(
                latitude = np.linspace(
                    latitudeOfFirstGridPoint, latitudeOfLastGridPoint, nbLat
                ),
                longitude = np.linspace(
                    longitudeOfFirstGridPoint, longitudeOfLastGridPoint, nbLon
                )
            ),
            attrs=dict(
                latitudeOfFirstGridPoint=latitudeOfFirstGridPoint,
                latitudeOfLastGridPoint=latitudeOfLastGridPoint,
                longitudeOfFirstGridPoint=longitudeOfFirstGridPoint,
                longitudeOfLastGridPoint=longitudeOfLastGridPoint,
                nbLat=nbLat,
                nbLon=nbLon
            )
        )

        self.compute = xr.Dataset(
            coords=dict(
                latitude = self.coords['latitude'].values,
                longitude = self.coords['longitude'].values,
                time = pd.date_range(start='1941-01-01', end='2024-12-31').to_numpy()
            )
        )
        
        pass



    def get_paths(self, pathListToData, onlyDirectory, resolution, years):

        pathsToFiles = {}                                                                           # Dict with self.fileList as keys and paths to files as values

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
        fileType = key[0]
        da = xr.open_dataarray(self.pathsToFiles[key])
        da = da.drop_vars(names="number", errors="ignore")
        if fileType == 'hindcast':                                                                  # Reindexing the ('hdate','time') dimension for hincast files
            da = reindex_hindcast(da)
        da.name = key
        return da


    def compute_time_max(self, **kwargs:str) -> xr.DataArray :
        ''' Compute the maximum in every files of the dataset and create a max dataset '''

        timeSelec = kwargs.get('timeSelec', None)

        max_datasets = []
        for key in self.fileList:
            data = self.open_data(key)
            if timeSelec:
                yearsList = np.array([pd.Timestamp(date).year for date in data['time'].values])
                if all(
                    any(y==yearsList) for y in timeSelec
                ):
                    data = data.sel(time=timeSelec)
                    max_datasets.append(data.max(dim='time').expand_dims('ref'))
            else:
                max_datasets.append(data.max(dim='time').expand_dims('ref'))
            data.close()

        max_array = xr.concat(max_datasets, dim='ref')
        return max_array.max(dim='ref', skipna=True)