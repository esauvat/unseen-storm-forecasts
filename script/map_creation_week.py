###   
###    Creation of Hans Storm weather week maps
###

import weatherdata as wd
from weatherdata import geographics as geo



# pathToFile = "unseen-storm-forecasts/hans_storm/tp24_0.25x0.25_2023.nc"
pathToFile = ("/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/continuous-format/daily/tp24/tp24_0.25x0"
              ".25_2023.nc")
days = wd.np.arange(217, 223)

totalPrecipitationsNo = wd.xr.open_dataarray(pathToFile)

size = 'large'
n, p = 2, 3

boundaries, cLat, cLon = wd.boundaries(totalPrecipitationsNo, 'largeNo')
effectSample = wd.select_sample(totalPrecipitationsNo, boundaries, days)
projLCoNo = geo.ccrs.LambertConformal(central_latitude=cLat, central_longitude=cLon)

###   Daily precipitations   ###

fig, axis = geo.map(n=n, p=p, size=size, boundaries=boundaries, proj=projLCoNo)
fig, axis = wd.showcase_data(totalPrecipitationsNo, effectSample, days, fig, axis)
i = 0
for ax in axis:
    ax.set_title(wd.nb_to_date(days[i], '2023'))
    i += 1
fig.suptitle('Daily total precipitation')

""" geo.plt.show() """
fig.savefig('unseen-storm-forecasts/maps/1d_tp/1d_tp_week')

###   3 days precipitations   ###

threeDaysAvgPrecipitationsNo = wd.mean_over_time(totalPrecipitationsNo, span=3)

# Average Precipitations

fig, axis = geo.map(n=n, p=p, size=size, boundaries=boundaries, proj=projLCoNo)

fig, axis = wd.showcase_data(threeDaysAvgPrecipitationsNo, boundaries, days, fig, axis)
i = 0
for ax in axis:
    ax.set_title(wd.nb_to_date(days[i], '2023'))
    i += 1
fig.suptitle('3 days average precipitation')

""" geo.plt.show() """
fig.savefig('unseen-storm-forecasts/maps/3d_tp/3d_avgp_week')
