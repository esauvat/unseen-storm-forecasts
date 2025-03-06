
###   
###   This is an annex for the weatherdata module
###

import os

from weatherdata import *


class composite_dataset :

    def __init__(self, pathToData:str, isDirectory:bool=False):
        paths = []
        if isDirectory or pathToData.endswith('/'):
            for filename in os.listdir(pathToData):
                paths.append(os.path.join(pathToData, filename))
        else:
            paths = open(pathToData, 'r').read().split('\n')
            if len(paths[-1]) == 0:
                paths.pop()
        
        self.pathList = np.array(paths)
        self.dims = Dataset(self.pathList[0], 'r').dimensions
        self.var = Dataset(self.pathList[0], 'r').variables

        pass

    