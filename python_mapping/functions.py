
''' Major functions of the wheaterdata module '''

import weatherdata_generic
import classes

import numpy as np, xarray as xr, pandas as pd
import geographics as geo


def draw_map(data:xr.DataArray, **kwargs) :
    ''' Given a set of data, draw the map(s) '''

    title = kwargs.get('title', None)
    times = kwargs.get('times', []) 
    coordsRange = kwargs.get('mapSize', "largeNo")                                              # The boundaries of the map in terms of geographic coordinates (default is all center and south of Norway)
    figSize = kwargs.get('figSize', "medium")
    extent = kwargs.get('extent', None)

    if 'time' in data.coords:
        nbMaps = len(data['time'].values)                                                       # Set the number of subplots and the grid dimension to fit the DataArrays
    else:
        nbMaps = 1
    nbRows, nbColumns = weatherdata_generic.mosaic_split(nbMaps)

    boundaries = weatherdata_generic.boundaries(data, size=coordsRange)[0]                      # Compute the map's boundaries to fit the dataset
    fig, axis = geo.map(nbRows, nbColumns, nbMaps, figSize, boundaries)                         # Create the map with proper size and geographical background
    fig, axis = weatherdata_generic.showcase_data(data, boundaries, fig, axis, nbMaps, extent=extent) # Plot the data

    if len(times)!=0:
        for i in range(nbMaps):                                                                 # If years have been specified
            axis[i].set_title(times[i])                                                         # Put the year as title for each subplot

    if title:
        fig.suptitle(title)                                                                     # If specified, set the figure title

    return fig, axis


def map_of_max(data:classes.composite_dataset, **kwargs):
    ''' Create a map of the the maximum recorded tp values '''

    months = kwargs.get('months', [])                                                           # Get the list of months ov which to compute the max
    splitYears = kwargs.get('splitYears', False)                                                # Choose if you want to plot each years in the years list, can't be use with months
    years = kwargs.get('years', [])                                                             # Get the list of years on which to compute the max
    timeSpan = kwargs.get('timeSpan', None)                                                     # And the number of years each sample last
    title = kwargs.get('title', None)                                                           # Title of the map (plt variable)
    coordsRange = kwargs.get('mapSize', "largeNo")                                              # The boundaries of the map in terms of geographic coordinates (default is all center and south of Norway)
    figSize = kwargs.get('figSize', "medium")                                                   # Size of the plt figure 
    directory = kwargs.get('dir', None)                                                         # Directory to store the map, is None the map is just shown
    splitPlot = kwargs.get('splitPlot', False) 

    assert len(months)==0 or not splitYears, " Can't plot annual and monthly at the same time "

    resolution = data.resolution                                                                # Get the dataset's resolution
    
    """ if name in data.compute.data_vars:                                                          # Check if the wanted values (eg max over all time) has already been computed
        max_simulated = data.compute[name]                                                      # If yes just access the data
        nbMaps = len(max_simulated['time'].values)                                              # And set the number of subplot and grid dimensions to fit the data
        nbRows, nbColumns = weatherdata_generic.mosaic_split(nbMaps)
    else: """                                                                                       # If no compute the data
    if splitYears:                                                                           # First case is if a set of years has been specified
        dataarrays = []                                                                             # Create a list to store the DataArrays before concatenation
        for y in years: 
            if timeSpan:                                                                            # If a timeSpan is specified
                yearsSample = [str(i) for i in range(int(y), int(y)+timeSpan)]                      # Create the list of years on which compute the max
                data_max = data.compute_time_max(timeRange=yearsSample)                             # And create the max DataArray
            else:   
                data_max = data.compute_time_max(timeRange=[y])                                     # If not just create the max DataArray for the specified year
            data_max = data_max.expand_dims({"time":[y]})                                           # Create a time dimension with label the specified year's first day to use as alignment when concatenating
                                                                                                    # the time is set as the year's first day to fit the data.compute coordinates when storing
            dataarrays.append(data_max.transpose("time", "latitude", "longitude"))  
            data_max.close()    
        max_simulated = xr.concat(dataarrays, dim="time")
        del dataarrays  
    elif len(months)!=0:                                                                        # Second case is when a set of months is specified
        dataarrays = []
        for m in months:
            if type(m) is list:
                data_max = data.compute_time_max(years, monthSelec=m)
            else:
                data_max = data.compute_time_max(years, monthSelec=[m])
            data_max = data_max.expand_dims({"time":[m]})
            dataarrays.append(data_max.transpose("time","latitude","longitude"))
            data_max.close()
        max_simulated = xr.concat(dataarrays, "time")
        del dataarrays
    else:                                                                                       # Third case is when no set of years is specified, ie we compute the max over all time
        max_simulated = data.compute_time_max(years)


    if not splitPlot:
        if not splitYears:
            times = months
        else:
            times = years
        fig, _ = draw_map(
            max_simulated, 
            title=title, 
            times=times, 
            mapSize=coordsRange, 
            figSize=figSize
        )

        if directory:                                                                           # If a directory is specified, we want to save the map in it, hence we create the map's file name
            timeReference, resReference = '', '_all-resolution'                                 # Initiate a time and resolution reference to insert in the name
            timeRangeReference = '_all-time'
            if not splitYears and len(months)!=0 and len(years)!=0:
                timeRangeReference = '_range-' + years[0] + '-' + years[-1]
                beginMonth = weatherdata_generic.alphaMonths[months[0]]
                endMonth = weatherdata_generic.alphaMonths[months[-1]]
                timeReference = '_' + beginMonth + '-' + endMonth
            elif not splitYears and len(years)!=0:
                timeRangeReference = '_range' + years[0] + '-' + years[-1]                      # If needed change the time reference as the years selected
            elif splitYears and len(years)!=0:
                timeRangeReference = ''
                timeReference = '_' + years[0] + '-' + years[-1]
            elif len(months)!=0:
                beginMonth = weatherdata_generic.alphaMonths[months[0]]
                endMonth = weatherdata_generic.alphaMonths[months[-1]]
                timeRangeReference = '_' + beginMonth + '-' + endMonth
            if resolution:
                resReference = '_' + resolution + 'x' + resolution                              # If needed specify the resolution

            fig.savefig(directory+'tp24-max' + resReference + timeReference + timeRangeReference + '.png')
    
        else:
            geo.plt.show()                                                                      # If no directory was given, just show the map

        geo.plt.close()
    
    else:                                                                                       # Repeat the previous step for all times                                             
        for time in max_simulated['time'].values:
            if not type(time) is str:
                alphaTime = weatherdata_generic.alphaMonths[time]
                data = max_simulated.sel(time=time)
                data = data.drop_vars("time").expand_dims({"time":[0]})
                fig, _ = draw_map(
                    data,
                    title=title+' : '+alphaTime,
                    mapSize=coordsRange,
                    figSize=figSize
                )
            else:
                alphaTime=time
                data = max_simulated.sel(time=time)
                data = data.drop_vars("time").expand_dims({"time":[0]})
                fig, _ = draw_map(
                    data,
                    title=title+' : '+alphaTime,
                    mapSize=coordsRange,
                    figSize=figSize
                )

            if directory:
                timeReference, resReference, timeRangeReference = '', '_all-resolution', '_all-time'
                if not splitYears and len(years)!=0: 
                    timeRangeReference = '_range-' + years[0] + '-' + years[-1]
                if splitYears or len(months)!=0:
                    timeReference = '_' + alphaTime
                if resolution:
                    resReference = '_' + resolution + 'x' + resolution

                fig.savefig(directory+'tp24-max' + resReference + timeReference + timeRangeReference + '.png')
        
            else:
                geo.plt.show()
    
    return max_simulated