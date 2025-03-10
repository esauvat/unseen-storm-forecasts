   
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



    def max(self, *args:str, **kwargs:np.float64) -> xr.Dataset :
        # TODO