from pysolar.solar import *
import datetime


def process_sun_position():

    date = datetime.datetime(2018, 1, 1, 00, 00, 00)
    tmp_date = datetime.datetime(2018, 1, 1, 00, 00, 00)
    sun_set = False
    sun_rise = False

    while True:
        while True:

            azimuth = convert_north(get_azimuth(46.20949, 6.135212, date))
            elevation = get_altitude(46.20949, 6.135212, date)
            date += datetime.timedelta(minutes=1)

            if elevation > 0 and not sun_rise:
                sun_rise = True
                sun_set = False
                print(f"Sun rise => Azimuth: {azimuth}\nElevation: {elevation}\nDate: {date}\n")

            if elevation < 0 and not sun_set:
                sun_rise = False
                sun_set = True
                print(f"Sun set => Azimuth: {azimuth}\nElevation: {elevation}\nDate: {date}\n")
                break
        tmp_date += datetime.timedelta(days=1)
        date = tmp_date

def get_sun_set():
    pass


def get_sun_rise():
    pass


# Convert azimuth south to north
def convert_north(south_azimuth):
    c = south_azimuth - 180
    if abs(c) > 360:
        c = south_azimuth + 180
        return abs(c)
    return abs(c)