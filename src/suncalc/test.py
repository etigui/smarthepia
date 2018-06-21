from pysolar.solar import *
import datetime
import numpy as np
import csv
import time

import matplotlib.pyplot as plt

def test():
    date = datetime.datetime(2018, 1, 1, 00,00,00)
    tmp_date = datetime.datetime(2018, 1, 1, 00, 00, 00)

    x = []
    i = 1
    y = []

    while True:
        while True:
            azimuth = convert_north(get_azimuth(46.20949, 6.135212, date))
            elevation = get_altitude(46.20949, 6.135212, date)
            if int(azimuth) == 180:
               #print(f"Azimuth: {azimuth} Date: {date}")
                i += 1
                x.append(i)
                y.append(date.minute)
                break
            date += datetime.timedelta(minutes=1)

        tmp_date += datetime.timedelta(days=1)
        date = tmp_date
        print(tmp_date)

        if tmp_date.year == 2019:
            plt.plot(x, y)
            plt.title("Solar azimuth vs. elevation angle")
            plt.xlabel("Elevation [deg]")
            plt.ylabel("Azimuth [deg]")
            plt.show()




        #print(f"Elevation: {elevation}")
        #print(f"Azimuth: {azimuth}")
        #print(f"Radiation: {rad}")

# Convert azimuth south to north
def convert_north(south_azimuth):
    c = south_azimuth - 180
    if abs(c) > 360:
        c = south_azimuth + 180
        return abs(c)
    return abs(c)

