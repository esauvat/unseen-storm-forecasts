
''' Major functions of the wheaterdata module '''

import weatherdata_generic
import classes

import numpy as np, xarray as xr, pandas as pd
import geographics as geo

def map_of_max(data:classes.composite_dataset, name:str, **kwargs):

    years = kwargs.get('years', [])
    timeSpan = kwargs.get('timeSpan', None)
    title = kwargs.get('title', None)
    resolution = kwargs.get('resolution', None)
    coordsRange = kwargs.get('mapSize', "largeNo")
    figSize = kwargs.get('figSize', "medium")
    directory = kwargs.get('dir', None)

    nbRows, nbColumns, nbMaps =  1, 1, 1
    
    if name in data.compute.data_vars:
        max_simulated = data.compute[name]
        nbMaps = len(max_simulated['time'].values)
        nbRows, nbColumns = weatherdata_generic.mosaic_split(nbMaps)
    else:
        if len(years)!=0:
            dataarrays = []
            for y in years:
                if timeSpan:
                    yearsSample = [str(i) for i in range(int(y), int(y)+timeSpan)]
                    data_max = data.compute_time_max(timeSelec=yearsSample)
                else:
                    data_max = data.compute_time_max(timeSelec=[y])
                    return data_max
                data_max = data_max.expand_dims({"time":[y]})
                dataarrays.append(data_max.transpose("time", "latitude", "longitude"))
            max_simulated = xr.concat(dataarrays, dim="time")
            nbMaps = len(max_simulated['time'].values)
            nbRows, nbColumns = weatherdata_generic.mosaic_split(nbMaps)
        else:
            max_simulated = data.compute_time_max()
        data.compute[name] = max_simulated

    boundaries = weatherdata_generic.boundaries(data, size=coordsRange)[0]

    fig, axis = geo.map(n=nbRows, p=nbColumns, nbMap=nbMaps, size=figSize, boundaries=boundaries)

    fig, axis = weatherdata_generic.showcase_data(max_simulated, boundaries, fig, axis, nbMaps)

    if len(years)!=0:
        for i in range(nbMaps):
            axis[i].set_title(years[i])
    elif title:
        fig.suptitle(title)

    if directory:
        timeReference, resReference = '_all-time', '_all-resolution'
        if len(years)!=0: 
            timeReference = '_' + years[0] + '-' + years[-1]
        if resolution:
            resReference = '_' + resolution + 'x' + resolution

        fig.savefig(directory+'tp24-max' + resReference + timeReference + '.png')
    
    else:
        geo.plt.show()

    geo.plt.close()