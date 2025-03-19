   
""" This is an annex for the weatherdata module """

from weatherdata_generic import *
import numpy as np, xarray as xr


class composite_dataset :

    ''' A python class to simplify operation on a multi-file dataset '''


    def __init__(self, pathListToData:list[str], reanalysis=True, resolution:str=None):
        
        self.resolution = resolution                                                                # Resolution of the data, if None, all resolutions are selected
        self.reanalysis = reanalysis

        self.pathsToFiles = self.get_paths(pathListToData, self.resolution)                         # Dict of (fileType,fileName) keys with pathToFile values
        self.fileList = [key for key in self.pathsToFiles.keys()]                                   # List of tuple (fileType,fileName)
        self.dims = ("latitude","longitude","time")                                                 # Tuple of dataset's dimension
        
        sample = xr.open_dataarray(self.pathsToFiles[self.fileList[0]])                             # Openning any data file to acces informations like the coordinates

        latitudeOfFirstGridPoint = sample['latitude'].values[0]                                     # Highest latitude  (Latitudes are stored in decreasing order)
        latitudeOfLastGridPoint = sample['latitude'].values[-1]                                     # Lowest latitude
        longitudeOfFirstGridPoint = sample['longitude'].values[0]                                   # Lowest longitude
        longitudeOfLastGridPoint = sample['longitude'].values[-1]                                   # Highest longitude

        if (not self.resolution=='0.5') and '0.5x0.5' in self.fileList[0][1]:                       # Checking if the sample file is in 0.5 resolution while other in the Dataset are in 0.25 resolution
            nbLat = 2*len(sample['latitude'].values)-1                                              # If so, we want the coordinates resolution to be twice as much as in the sample file
            nbLon = 2*len(sample['longitude'].values)-1                                             # to fit with all format in the dataset (through reindexing for the 0.5 resolution files)
        else:
            nbLat = len(sample['latitude'].values)                                                  # Id not, we just copy the coordinates for the dataset
            nbLon = len(sample['longitude'].values)

        self.coords = xr.DataArray(                                                                 # coords Array for quicker access to the dataset's properties
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

        self.compute = dict()                                                                       # compute dict links already computed arrays such as max over time to pkl file's addresses
        
        pass



    def get_paths(self, pathListToData, resolution):
        ''' Creating the pathsToFiles dict to store paths to access the datas '''

        pathsToFiles = {}                                                                           # Initiating dict

        for loc in pathListToData:                                                                  # Loop over all the addresses passed as arguments
            if loc.endswith('/'):                                                                   # Check if the address is a directory
                extract_files(loc, pathsToFiles)                                                    
            else:                                                                                   # or if it's a txt file with paths on it
                txtAsList = open(loc, 'r').read().split('\n')
                if txtAsList[-1] == '':                                                             # Remove the last line if it's empty    
                    del txtAsList[-1]
                for fileLoc in txtAsList:
                    fileLocScatter = fileLoc.split('/')                                             # Get the directories tree above the data
                    filename = fileLocScatter.pop()                                                 # Store the name of the file
                    type = ''
                    while fileLocScatter != []:                                                     # Iterate over the path tree's nodes to find the file type
                        dir = fileLocScatter.pop()
                        if dir in ['forecast','hindcast','continuous-format','continuous']:         # Detect if a type corresponding directory is in the path tree
                            type = dir                                                              # If so store the type of the file
                            break
                    assert type != '', "Wrong file path in the document"                            # Assert that a type as been found
                    pathsToFiles[(type, filename[:-3])] = fileLoc                                   # Create the key-value instance (NB: We remove the .nc in the file name)

        if resolution:                                                                              # Remove the unwanted files if a resolution is specified
            keysToDel = []
            for key in pathsToFiles.keys():
                if not resolution in key[1]:                                                        # Check if the file as the right resolution
                    keysToDel.append(key)                                                           
            for key in keysToDel:                                                                   # If not remove the corresponding key-value
                del pathsToFiles[key]
        
        return pathsToFiles
    

    def open_data(self, key:tuple[str,str]) -> xr.DataArray:
        ''' Open "file" as DataArray and reshape it to fit the class attributes '''

        """ # Relevant when the 'if fileType=='hindcast' part will have been reworked
        fileType, fileName = key """
        
        fileType, fileName = key
        da = xr.open_dataarray(self.pathsToFiles[key])
        if self.reanalysis:
            da = da.drop_vars(names="number", errors="ignore")                                      # If the dataset is a reanalysis' one, remove the "number" dimension if it exists

        """ # This needs to be reworked 
        if fileType == 'hindcast':                                                                  # Reindexing the ('hdate','time') dimension for hincast files
            da = reindex_hindcast(da) """
        
        if (not self.resolution=='0.5') and '0.5' in fileName:                                      # Checking if the data is with 0.5 resolution while the dataset is with 0.25 one
            da = da.reindex(dict(                                                                   # If so, reindex (the missing values are filled with np.nan)
                latitude=self.coords['latitude'],
                longitude=self.coords['longitude']
            ))
        da.name = fileType + '-' + fileName                                                         # Change DataArray name for (fileType,fileName) tuple
        return da


    def compute_time_max(self, **kwargs:str) -> xr.DataArray :
        ''' Compute the maximum in every files of the dataset and create a max dataset '''

        yearSelec = kwargs.get('yearSelec', None)                                                   # Check if a specific years list is asked
        monthSelec = kwargs.get('monthSelec', None)                                                 # Check if a specific months list is asked
        meanSpan = kwargs.get('meanSpan', None)                                                     # Check if a mean length is asked

        max_datasets = []                                                                           # Initiate a list to store the max_datasets before concatenation
        for key in self.fileList:
            data = self.open_data(key)                                                              # Open each data file
            if meanSpan:
                data = mean_over_time(data, meanSpan)                                               # Turn the data into means, did at this time to avoid most edge effects, but takes more time. 
            if yearSelec:                                                                               # Care for edge effects at early Januar and end of December.
                data = data.sel(time=slice(yearSelec[0],yearSelec[-1]))                             # If needed, select the requested time list
            if monthSelec:                                                                          # Same for months
                def choose_month(m:int):
                    first, last = monthSelec[0], monthSelec[-1]
                    return (m>=first) & (m<=last)
                data = data.sel(time=choose_month(data['time.month']))
            if data['time'].shape!= (0,):                                                           # Check if the previous selection is not empty
                max_datasets.append(data.max(dim='time').expand_dims({'ref':[key]}))                        # If not, compute the maximum and add it the tho max_datasets list
            data.close()                                                                            # Close each data file after computation to free the memory

        max_array = xr.concat(max_datasets, dim='ref')                                              # Concatenate the max_arrays 
        del max_datasets
        return max_array.max(dim='ref', skipna=True)                                                # to return the max over all the dataset