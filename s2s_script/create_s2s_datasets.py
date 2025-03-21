
''' Creation of s2s' weathersets 0'''

import sys

sys.path.append('/nird/projects/NS9873K/emile/unseen-storm-forecasts/python_mapping/')

import weatherdata as wd
import pickle


###   Setting variables

dirs = ['/nird/projects/NS9873K/etdu/processed/cf-forsikring/s2s/ecmwf/forecast/daily/values/tp24/',
        '/nird/projects/NS9873K/etdu/processed/cf-forsikring/s2s/ecmwf/hindcast/daily/values/tp24/']


###   Creation of the datasets

hRes = wd.Weatherset(dirs, reanalysis=False, resolution='0.25', multiType=True)
lRes = wd.Weatherset(dirs, reanalysis=False, resolution='0.5', multiType=True)


###   Saving

with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_0.25.pkl', 'wb') as outp:
    pickle.dump(hRes, outp, pickle.HIGHEST_PROTOCOL)
with open('/nird/projects/NS9873K/emile/unseen-storm-forecasts/weathersets/s2s_0.5.pkl', 'wb') as outp:
    pickle.dump(lRes, outp, pickle.HIGHEST_PROTOCOL)