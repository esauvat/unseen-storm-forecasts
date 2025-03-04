
import weatherdata as wd
from map import *


def time_avg_data():
    global totalPrecipitation
    totalPrecipitation = wd.mean_over_time(totalPrecipitation, span=timeSpan)

def time_sum_data():
    global totalPrecipitation
    totalPrecipitation = wd.sum_over_time(totalPrecipitation, span=timeSpan)

def space_avg_data():
    global totalPrecipitation
    totalPrecipitation = wd.mean_over_space(totalPrecipitation, span=timeSpan)

def space_sum_data():
    global totalPrecipitation
    totalPrecipitation = wd.sum_over_space(totalPrecipitation, span=timeSpan)

def get_data():
    if type=="time_avg":
        time_avg_data()
    elif type=="time_sum":
        time_sum_data()
    elif type=="space_avg":
        space_avg_data()
    elif type=="space_sum":
        space_sum_data()