import sys
sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/python_mapping')

import pickle
import numpy as np, xarray as xr
import weatherdata

with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_0.5.pkl', 'rb') as inp:
    tpSet = pickle.load(inp)


for key in tpSet.fileList:
    if ('2023' in key[1]) and (key[0]=='forecast'):
        print(key[1])
        data = xr.open_dataarray(tpSet.pathsToFiles[key])
        print(data['number'].values.shape)