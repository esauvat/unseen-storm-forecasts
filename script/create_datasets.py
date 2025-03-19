
''' Create the datasets for data persistance '''

import sys

sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/python_mapping/')

import pickle
import weatherdata as wd

directory = '/nird/projects/NS9873K/etdu/processed/cf-forsikring/era5/continuous-format/daily/tp24/'


with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/continuous_0.5.pkl', 'wb') as outp:
    tpSet = wd.Weatherset([directory], resolution='0.5')
    pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)

del tpSet


with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/continuous_0.25.pkl', 'wb') as outp:
    tpSet = wd.Weatherset([directory], resolution='0.25')
    pickle.dump(tpSet, outp, pickle.HIGHEST_PROTOCOL)

del tpSet