from pysolar.solar import *
import datetime
import numpy as np
import csv
import time
import test

import matplotlib.pyplot as plt

def main():
    test.test()
    date = datetime.datetime(2018, 6, 19, 00,00,00)

    lel = []
    lalt = []
    ldate = []
    while True:
        date += datetime.timedelta(minutes=6)
        elevation = get_altitude(46.20949, 6.135212, date)
        azimuth = convert_north(get_azimuth(46.20949, 6.135212, date))


        fields = [date, "{:.4f}".format(elevation), "{:.4f}".format(azimuth)]
        with open(r'data.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(fields)

        lel.append(elevation)
        lalt.append(azimuth)

        #if date.hour == 0 and date.minute == 0:
        #    break

        if date.hour == 12 and date.minute == 0:
            print(f"Azimuth: {azimuth} Date: {date}")


    #plt.plot(lel, lalt)
    #plt.title("Solar azimuth vs. elevation angle")
    #plt.xlabel("Elevation [deg]")
    #plt.ylabel("Azimuth [deg]")
    #plt.show()


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




if __name__ == "__main__":
    main()