# 
# Script to plot the final results of the unseen method
# 
# The first plot displays the distribution of the worst events for each month and each years, 
# through a boxplot with the distribution of worst events for each month. We use a boxplot rather
# than a violin plot because we are only interested in the extrem values.
# 
# The second plot displays the return period of the events, for each month. Specificaly the graph will
# be of the curve amount of precipitation vs return period.
#

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
import sys
sys.path.append("/nird/projects/NS9873K/emile/unseen-storm-forecasts")

import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import cast
from scipy.stats import gumbel_r, genextreme

from weatherdata.geographics import apply_curv_weights
from weatherdata import sum_over_time



##########################################################################
#
#       Functions
#

def plot_distribution(
        da: xr.DataArray,
        threshold: float,
        output_dir = 'final_results',
        filename = 'worst_event_distribution'
) -> None:
    """Plot the distribution of the worst events, for each month between May and October, adding a 
        threshold to mark Hans storm.

    Args:
        da (xr.DataArray): DataArray of the modelled worst events with dimensions ("date", "number").
            The "date" dimension must have two coordinates "date" and "month", the second one storing
            the information of the mosts overlapping month of the modelled time extent.
    """
    
    # Ensure the necessary coordinate exists
    if 'month' not in da.coords:
        raise ValueError("The DataArray must have a 'month' coordinate.")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Select only months from May (5) to October (10)
    targeted_months = [5, 6, 7, 8, 9, 10]
    da_filtered = da.sel(date=da['month'].isin(targeted_months))

    # Convert to a DataFrame for plotting
    df = da_filtered.to_dataframe(name='value').reset_index()

    # Set the plotting style
    sns.set_theme(style="whitegrid")

    # Create the boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='month', y='value', data=df, palette='coolwarm')
    
    # Mark Hans storm
    plt.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Hans: {threshold:.1f}')
    plt.legend()
    
    # # Count the number of Hans-exceeding events
    # exceed = da_filtered.where(da_filtered>threshold, drop=True)
    # monthly_exceeding = [
    #     exceed.where(exceed.month==m, drop=True).values.flatten()
    #     for m in targeted_months
    # ]
    # exceed_amount = [
    #     len(vals[~np.isnan(vals)])
    #     for vals in monthly_exceeding
    # ]
    # for i in range(len(targeted_months)):
    #     plt.text(i+0.05, threshold*1.01, str(exceed_amount[i]), color='red')
    
    # Set labels and title
    plt.xlabel('')
    plt.xticks(ticks= list(range(6)), labels= ["May", "June", "July", "August", "September", "October"], rotation=45)
    plt.ylabel('Accumulated precipitations (mm)')
    plt.title('Distribution of Worst Events from May to October')

    # Show the plot
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, filename + '.png')
    )
    plt.close()
    
    pass


def plot_retper(
        da:xr.DataArray,
        threshold: float,
        output_dir = 'final_results',
        filename = 'worst_event_retper'
) -> None:
    """Plot the return period of the events, for each month between May and October, adding a 
        threshold to mark Hans storm.

    Args:
        da (xr.DataArray): DataArray of the modelled worst events, with dimensions ("date", "number").
            The "date" dimension must have two coordinates "date" and "month", the second one storing
            the information of the mosts overlapping month of the modelled time extent.
        threshold (float): Value of the mark (most often representing Hans)
        output_dir (str, optional): Directory to store the plot. Defaults to 'final_results'.
    """
    
    # Ensure the necessary coordinate exists
    if 'month' not in da.coords:
        raise ValueError("The DataArray must have a 'month' coordinate.")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Select only months from May (5) to October (10)
    targeted_months = {5:"May", 6:"June", 7:"July", 8:"August", 9:"September", 10:"October"}
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    for m in targeted_months.keys():
        
        # Select data
        da_month = da.sel(date=(da['month']==m))
        
        # Sort in descending order
        sorted_events = np.sort(da_month.values.flatten())[::-1]
        sorted_events = sorted_events[~np.isnan(sorted_events)]
        n = len(sorted_events)
        ranks = np.arange(1, n+1)
        
        if n < 2: # Need at least 2 points to fit
            continue
            
        # Weibull return period
        retper = (n+1)/ranks
        
        # Get the next color in the matplotlib cycle
        color = ax._get_lines.get_next_color() # type: ignore
        
        # Fit Gumbel distribution to monthly data
        
        loc, scale = gumbel_r.fit(sorted_events)
        
        # Smooth curve
        x_smooth = np.linspace(sorted_events.min(), sorted_events.max(), 200)
        cdf = gumbel_r.cdf(x_smooth, loc=loc, scale=scale)
        retper_smooth = 1 / (1 - cdf)
        
        ax.semilogy(x_smooth, retper_smooth, label=f"{targeted_months[m]}", linestyle='-', color=color)
        
        # # Plot empirical points
        # ax.semilogy(sorted_events, retper, linestyle='--', alpha=0.5, color=color)

    # Add Hans marker
    ax.axvline(threshold, color='red', linestyle='--')
    ax.text(threshold, 1, "Hans", color='red', rotation=-90, va='bottom')
    
    # Figure attributes
    plt.legend()
    plt.xlabel('Accumulated precipitations (mm)')
    plt.ylabel('Peturn Period (years)')
    plt.title('Return Period vs. Precipitation')
    plt.grid(True, which='major', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, filename+'.png')
    )
    plt.close()
    
    pass


def plot_retper_GEV(
        da:xr.DataArray,
        threshold: float,
        output_dir = 'final_results',
        filename = 'worst_event_retper'
) -> None:
    """Plot the return period of the events, for each month between May and October, adding a 
        threshold to mark Hans storm.

    Args:
        da (xr.DataArray): DataArray of the modelled worst events, with dimensions ("date", "number").
            The "date" dimension must have two coordinates "date" and "month", the second one storing
            the information of the mosts overlapping month of the modelled time extent.
        threshold (float): Value of the mark (most often representing Hans)
        output_dir (str, optional): Directory to store the plot. Defaults to 'final_results'.
    """
    
    # Ensure the necessary coordinate exists
    if 'month' not in da.coords:
        raise ValueError("The DataArray must have a 'month' coordinate.")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Select only months from May (5) to October (10)
    targeted_months = {5:"May", 6:"June", 7:"July", 8:"August", 9:"September", 10:"October"}
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    for m in targeted_months.keys():
        
        # Select data
        da_month = da.sel(date=(da['month']==m))
        
        # Sort in descending order
        sorted_events = np.sort(da_month.values.flatten())[::-1]
        sorted_events = sorted_events[~np.isnan(sorted_events)]
        n = len(sorted_events)
        ranks = np.arange(1, n+1)
        
        if n < 2: # Need at least 2 points to fit
            continue
            
        # Weibull return period
        retper = (n+1)/ranks
        
        # Get the next color in the matplotlib cycle
        color = ax._get_lines.get_next_color() # type: ignore
        
        # Fit GEV distribution to monthly data
        
        c, loc, scale = genextreme.fit(sorted_events)
        
        # Smooth curve
        x_smooth = np.linspace(sorted_events.min(), sorted_events.max(), 200)
        cdf = genextreme.cdf(x_smooth, c, loc=loc, scale=scale)
        retper_smooth = 1 / (1 - cdf)
        
        ax.semilogy(x_smooth, retper_smooth, label=f"{targeted_months[m]}", linestyle='-', color=color)
        
        # Plot empirical points
        ax.semilogy(sorted_events, retper, linestyle='--', alpha=0.5, color=color)

    # Add Hans marker
    ax.axvline(threshold, color='red', linestyle='--')
    ax.text(threshold, 1, "Hans", color='red', rotation=-90, va='bottom')
    
    # Figure attributes
    plt.legend()
    plt.xlabel('Accumulated precipitations (mm)')
    plt.ylabel('Peturn Period (years)')
    plt.title('Return Period vs. Precipitation')
    plt.grid(True, which='major', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, filename+'.png')
    )
    plt.close()
    
    pass
    


########################################################################
#
#       Run the script
#



if __name__=="__main__":

    era5_2023 = xr.open_dataarray(
        '/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/continuous-format/daily/tp24/tp24_0.5x0.5_2023.nc'
    ).sel(
        latitude=slice(62.5,60.5),
        longitude=slice(9,11.5)
    )

    era5_2023 = cast(
        xr.DataArray,
        apply_curv_weights(
            era5_2023
        )
    ).mean(
        dim=["latitude", "longitude"]
    ) * 1000

    hans_val = sum_over_time(
        era5_2023.sel(
            time = slice(
                np.datetime64('2023-08-07'),
                np.datetime64('2023-08-09')
            )
        ),
        span=3, edges=False
    ).values[0]
    
    if len(sys.argv) >=2 and sys.argv[1]=="corrected":
        data = xr.open_dataarray(
            'data/maxs-corrected.nc'
        )
        
        plot_distribution(
            data, hans_val, 
            filename="worst_event_distribution_corrected"
        )
        
        plot_retper(
            data, hans_val,
            filename="worst_event_retper_corrected"
        )
        
    else:
        data = xr.open_dataarray(
            'data/maxs-full.nc'
        )
        
        plot_distribution(data, hans_val)
        
        plot_retper(data, hans_val)