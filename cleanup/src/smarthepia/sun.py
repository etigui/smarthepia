from pysolar.solar import *
import datetime

# Local import
import const
import random

# Angle
elevation_min = 6
elevation_max = 85
azimuth_min_max = 85

# Season
season_winter = "winter"
season_spring = "spring"
season_summer = "summer"
season_autumn = "autumn"


def check_sun():

    for i in range(-10, 370):
        res = is_sun_in_room(i)
        print(f"{i} {res}")


# Check if the sun is in the room
def is_sun_in_room(room_azimuth_angle):
    try:

        # Convert angle to int
        # If fail => return false and -1
        angle = int(room_azimuth_angle)

        # Check if angle is good otherwise return false and -1
        if 0 <= angle <= 360:
            if calc_room_elevation_angle() and calc_room_azimuth_angle(angle):
                return True, 0
            else:
                return False, 0
        return False, -1
    except ValueError:
        return False, -1


# Calc the min and max azimuth angle to det if the sun is going through the room
def calc_room_azimuth_angle(room_azimuth_angle: int):
    sun_azimuth = get_sun_azimuth()

    min_angle_status, min_angle = bound_angle(room_azimuth_angle - azimuth_min_max)
    max_angle_status, max_angle = bound_angle(room_azimuth_angle + azimuth_min_max)
    if min_angle_status and max_angle_status:
        if min_angle <= sun_azimuth <= max_angle:
            print(f" Az: {sun_azimuth}")
            return True
    return False


# Calc the min and max elevation angle to det if the sun is going through the room
def calc_room_elevation_angle():

    # Get sun elevation and check if between min and max
    sun_elevation = get_sun_elevation()
    if elevation_min <= sun_elevation <= elevation_max:
        print(f" El: {sun_elevation}")
        return True
    return False


# Get sun azimuth from lat/lon and current datetime
def get_sun_azimuth():
    return convert_north(get_azimuth(const.lat, const.lon, datetime.datetime.now()))


# Get sun elevation from lat/lon and current datetime
def get_sun_elevation():
    return get_altitude(const.lat, const.lon, datetime.datetime.now())


# Convert azimuth south to north
def convert_north(south_azimuth):
    c = south_azimuth - 180
    if abs(c) > 360:
        c = south_azimuth + 180
        return abs(c)
    return abs(c)


# Bound angle after add sub min max angle
def bound_angle(angle: int):
    if angle > 360:
        return True, (angle - 360)
    elif angle < 0:
        return True, abs(angle)
    else:
        return True, angle


# Get season from time
def get_season(now):

    Y = 2000  # dummy leap year to allow input X-02-29 (leap day)
    seasons = [(season_winter, (datetime.date(Y, 1, 1), datetime.date(Y, 3, 20))),
               (season_spring, (datetime.date(Y, 3, 21), datetime.date(Y, 6, 20))),
               (season_summer, (datetime.date(Y, 6, 21), datetime.date(Y, 9, 22))),
               (season_autumn, (datetime.date(Y, 9, 23), datetime.date(Y, 12, 20))),
               (season_winter, (datetime.date(Y, 12, 21), datetime.date(Y, 12, 31)))]

    if isinstance(now, datetime.datetime):
        now = now.date()
    now = now.replace(year=Y)
    return next(season for season, (start, end) in seasons if start <= now <= end)