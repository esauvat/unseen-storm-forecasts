###   
###    Creation of Hans Storm weather week maps
###

import sys

sys.path.append('/home/esauvat/Documents/NORCE - Extrem weather forecasting/unseen-storm-forecasts/python_mapping_tools')
sys.path.append('/nird/projects/NSS9873K/emile/unseen-storm-forecasts/python_mapping_tools')

import weatherdata as wd
import maps as mp

# pathToFile = "unseen-storm-forecasts/hans_storm/tp24_0.25x0.25_2023.nc"
pathToFile = "/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/continuous-format/daily/tp24/tp24_0.25x0.25_2023.nc"
days = wd.np.arange(217,223)

ncData = wd.Dataset(pathToFile, 'r')
totalPrecipitationsNo = wd.dataset_to_xr(ncData)

size = 'large'
n, p = 2, 3

boundaries, cLat, cLon = wd.boundaries(ncData, 'largeNo')
effectSample = wd.select_sample(totalPrecipitationsNo, boundaries, days)
projLCoNo = mp.ccrs.LambertConformal(central_latitude=cLat, central_longitude=cLon)


###   Daily precipitations   ###

fig, axis = mp.map(n=n, p=p, size=size, boundaries = boundaries, proj=projLCoNo)
fig, axis = wd.showcase_data(totalPrecipitationsNo, effectSample, days, fig, axis)
i=0
for ax in axis :
    ax.set_title(wd.nbToDate(days[i], '2023'))
    i+=1
fig.suptitle('Daily total precipitation')

""" mp.plt.show() """
fig.savefig('unseen-storm-forecasts/hans_storm/maps/1d_tp/1d_tp_week')


###   3 days precipitations   ###

threeDaysTotalPrecipitationsNo = wd.sum_over_time(totalPrecipitationsNo, span=3)
threeDaysAvgPrecipitationsNo = wd.mean_over_time(totalPrecipitationsNo, span=3)

# Total Precipitations

fig, axis = mp.map(n=n, p=p, size=size, boundaries = boundaries, proj=projLCoNo)

fig, axis = wd.showcase_data(threeDaysTotalPrecipitationsNo, boundaries, days, fig, axis)
i=0
for ax in axis :
    ax.set_title(wd.nbToDate(days[i], '2023'))
    i+=1
fig.suptitle('3 days total precipitation')

""" mp.plt.show() """
fig.savefig('unseen-storm-forecasts/hans_storm/maps/3d_tp/3d_tp_week')

# Average Precipitations

fig, axis = mp.map(n=n, p=p, size=size, boundaries = boundaries, proj=projLCoNo)

fig, axis = wd.showcase_data(threeDaysAvgPrecipitationsNo, boundaries, days, fig, axis)
i=0
for ax in axis :
    ax.set_title(wd.nbToDate(days[i], '2023'))
    i+=1
fig.suptitle('3 days average precipitation')

""" mp.plt.show() """
fig.savefig('unseen-storm-forecasts/hans_storm/maps/3d_tp/3d_avgp_week')