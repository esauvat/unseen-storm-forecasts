
''' Major functions of the wheaterdata module '''

import weatherdata_generic
import classes

import numpy as np, xarray as xr, pandas as pd
import geographics as geo

def map_of_max(data:classes.composite_dataset, name:str, **kwargs):
    ''' Create a map of the the maximum recorded tp values '''

    years = kwargs.get('years', [])                                                             # Get the list of years on which to compute the max
    timeSpan = kwargs.get('timeSpan', None)                                                     # And the number of years each sample last
    title = kwargs.get('title', None)                                                           # Title of the map (plt variable)
    coordsRange = kwargs.get('mapSize', "largeNo")                                              # The boundaries of the map in terms of geographic coordinates (default is all center and south of Norway)
    figSize = kwargs.get('figSize', "medium")                                                   # Size of the plt figure 
    directory = kwargs.get('dir', None)                                                         # Directory to store the map, is None the map is just shown 

    resolution = data.resolution                                                                # Get the dataset's resolution

    nbRows, nbColumns, nbMaps =  1, 1, 1                                                        # Initiate the number of subplots and the grid dimension, default is for a single map
    
    if name in data.compute.data_vars:                                                          # Check if the wanted values (eg max over all time) has already been computed
        max_simulated = data.compute[name]                                                      # If yes just access the data
        nbMaps = len(max_simulated['time'].values)                                              # And set the number of subplot and grid dimensions to fit the data
        nbRows, nbColumns = weatherdata_generic.mosaic_split(nbMaps)
    else:                                                                                       # If no compute the data
        if len(years)!=0:                                                                       # First case is if a set of years has been specified
            dataarrays = []                                                                         # Create a list to store the DataArrays before concatenation
            for y in years:
                if timeSpan:                                                                        # If a timeSpan is specified
                    yearsSample = [str(i) for i in range(int(y), int(y)+timeSpan)]                  # Create the list of years on which compute the max
                    data_max = data.compute_time_max(timeSelec=yearsSample)                         # And create the max DataArray
                else:
                    data_max = data.compute_time_max(timeSelec=[y])                                 # If not just create the max DataArray for the specified year
                data_max = data_max.expand_dims({"time":[np.datetime64(y+'-01-01')]})               # Create a time dimension with label the specified year's first day to use as alignment when concatenating
                                                                                                    # the time is set as the year's first day to fit the data.compute coordinates when storing
                dataarrays.append(data_max.transpose("time", "latitude", "longitude"))
            max_simulated = xr.concat(dataarrays, dim="time")
            nbMaps = len(max_simulated['time'].values)                                              # Set the number of subplots and the grid dimension to fit the DataArrays
            nbRows, nbColumns = weatherdata_generic.mosaic_split(nbMaps)
        else:                                                                                   # Second case is when no set of years is specified, ie we compute the max over all time
            max_simulated = data.compute_time_max()
        data.compute[name] = max_simulated                                                      # Store the computed Array for quicker access if needed later

    boundaries = weatherdata_generic.boundaries(data, size=coordsRange)[0]                      # Compute the map's boundaries to fit the dataset
    fig, axis = geo.map(nbRows, nbColumns, nbMaps, figSize, boundaries)                         # Create the map with proper size and geographical background
    fig, axis = weatherdata_generic.showcase_data(max_simulated, boundaries, fig, axis, nbMaps) # Plot the data

    if len(years)!=0:
        for i in range(nbMaps):                                                                 # If years have been specified
            axis[i].set_title(years[i])                                                         # Put the year as title for each subplot

    if title:
        fig.suptitle(title)                                                                     # If specified, set the figure title

    if directory:                                                                               # If a directory is specified, we want to save the map in it, hence we create the map's file name
        timeReference, resReference = '_all-time', '_all-resolution'                            # Initiate a time and resolution reference to insert in the name
        if len(years)!=0:
            timeReference = '_' + years[0] + '-' + years[-1]                                    # If needed change the time reference as the years selected
        if resolution:
            resReference = '_' + resolution + 'x' + resolution                                  # If needed specify the resolution

        fig.savefig(directory+'tp24-max' + resReference + timeReference + '.png')               # Save the map(s)
    
    else:
        geo.plt.show()                                                                          # If no directory was given, just show the map

    geo.plt.close()