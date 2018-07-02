import time
import datetime

# Local import
import utils
import const


# https://openweathermap.org API key
api_key = "adeaa68b9d2f5a100919934788d350e0"

# Position weather station id
city_id_meyrin = "2659667"
city_id_geneva = "2660646"

# Aip return error/success
return_code_limitation = 429
return_code_success = 200

# Weather condition ids
# https://openweathermap.org/weather-conditions
condition_thunderstorm_id = "200"
condition_drizzle_id = "300"
condition_rain_id = "500"
condition_clear_sky_id = "800"
condition_mist_id = "701"
condition_clouds_level_id = {"800": 0, "801": 1, "802": 2, "803": 3, "804": 4}

# Openweathermap routes
def route_current_weather_city():
    return f"http://api.openweathermap.org/data/2.5/weather?id={city_id_geneva}&appid={api_key}"


def route_forecast_city():
    return f"http://api.openweathermap.org/data/2.5/forecast?id={city_id_geneva}&appid={api_key}"


def route_current_weather_coordinates():
    return f"http://api.openweathermap.org/data/2.5/weather?lat={str(const.lat)}&lon={str(const.lon)}&appid={api_key}"


def route_forecast_coordinates():
    return f"http://api.openweathermap.org/data/2.5/forecast?lat={str(const.lat)}&lon={str(const.lon)}&appid={api_key}"


# Check if it's raining
def is_raining_drizzle(weather_id: str):

    # Prevent error
    if len(weather_id) > 1:

        # Check if rain or drizzle
        # Check the first char eg: condition_rain_id => 500 -> 599 => 5
        if str(weather_id)[0] == condition_thunderstorm_id[0] or str(weather_id)[0] == condition_drizzle_id[0] or str(weather_id)[0] == condition_thunderstorm_id[0]:
            return True
    return False


# Check if the sky is clear
# If cloud
def is_cloudy(weather_id):

    # Check if key exist
    # Check if cloudy or if there is mist
    if str(weather_id) in condition_clouds_level_id:
        cloud_level = condition_clouds_level_id[str(weather_id)]
        if cloud_level == 4:
            return True
    return False


# Check if mist
def is_mist(weather_id):
    if str(weather_id) == condition_mist_id:
        return True
    return False


# Get current weather
def get_api_current_weather():

    # Check if the API return good value
    status, js = utils.http_get_request_json(route_current_weather_coordinates())
    if status:
        if "cod" in js:
            try:
                if int(js['cod']) == return_code_success:
                    return True, js
            except ValueError:
                return False, None
    return False, None


# Get forecast (5 days every 3h)
def get_api_forecast():

    # Check if the API return good value
    status, js = utils.http_get_request_json(route_forecast_coordinates())
    if status:
        if "cod" in js:
            try:
                if int(js['cod']) == return_code_success:
                    return True, js
            except ValueError:
                return False, None
    return False, None


# Convert fahrenheit to celsius
def get_degree_from_fahrenheit(fahrenheit: float):
    return (fahrenheit - 32) / 1.8


# Convert kelvin to celsius
def get_degree_from_kelvin(kelvin: float):
    return kelvin - 273.15


# Check if we are in night time => close all blinds
def check_night_time(rule_day_time, rule_night_time):

    # Get current date and convert day and night time to time()
    time_now = datetime.datetime.now().time()
    night_time = datetime.datetime.strptime(f"{rule_night_time}:00", '%H:%M:%S').time()
    day_time = datetime.datetime.strptime(f"{rule_day_time}:00", '%H:%M:%S').time()

    before_midnight = datetime.datetime.strptime(f"23:59:59", '%H:%M:%S').time()
    midnight = datetime.datetime.strptime(f"00:00:00", '%H:%M:%S').time()
    after_midnight = datetime.datetime.strptime(f"00:00:01", '%H:%M:%S').time()

    # Sleep 1 sec if 00:00:00
    if time_now == midnight:
        time.sleep(1)

    # We are in new day
    nt = True
    if time_now >= after_midnight:
        if time_now > day_time:
            nt = False
        else:
            nt = True

    elif time_now <= before_midnight:
        if time_now > night_time:
            nt = True
        else:
            nt = False

    return nt

    # If we are during the night period
    # Between => eg: 23:00:00 => 08:00:00
    #if night_time <= time_now <= day_time:
    #    return True
    #return False


# Get last current weather measure from db
def get_db_current_weather(db):
    return db.sh.apicurrents.find_one({'$query': {}, '$orderby': {'$natural': -1}})


# Get last forecast measure from db
def get_db_forecast(db):
    return db.sh.apiforecast.find_one({'$query': {}, '$orderby': {'$natural': -1}})

# Get last forecast from api or db if fail
def get_forecast(db, log, local):

    # Get last forecast from db
    # TODO remove after
    if not local:

        # If error we get last data from db
        status, api_datas = get_api_forecast()
        if status:
            db.sh.apiforecast.insert(api_datas)
            return api_datas
        else:
            log.log_error(f"In function (get_forecast), API measure available")
            return get_db_forecast(db)
    else:
        return get_db_forecast(db)

# Get last current weather from api or db if fail
def get_current_weather(db, log, local):

    # Get last measures from db
    db_datas = get_db_current_weather(db)

    # Get last measures from db
    # TODO remove after
    if not local:

        # Get last measures from api
        status, api_datas = get_api_current_weather()

        # If get measures from api
        if status:

            # If the api have a new measures then we add it to the db and return it
            # Else give last measure from db
            if datetime.datetime.fromtimestamp(int(db_datas['dt'])) < datetime.datetime.fromtimestamp(int(api_datas['dt'])):
                db.sh.apicurrents.insert(api_datas)
                return api_datas
            else:
                return db_datas
        else:
            log.log_error(f"In function (get_current_weather), API measure available")
            return db_datas
    else:
        return db_datas


# Check if the curretn weather from DB/API are good
def get_check_current_weather(log, weather_current):

    # Check if data have been setted
    if weather_current is not None:

        # Get current weather
        datas = weather_current
        if 'dt' in datas:

            # Check if Weather API/DB return good value
            now_diff = datetime.datetime.now() - datetime.timedelta(hours=4)
            if datetime.datetime.fromtimestamp(int(datas['dt'])) > now_diff:
                return True, datas
            else:
                log.log_error(f"In function (get_check_current_weather) weather API/DB return bad updated value")
                return False, None
        else:
            log.log_error(f"In function (get_check_current_weather) weather data error")
            return False, None
    else:
        log.log_error(f"In function (get_check_current_weather) weather data are None")
        return False, None


# Check if current time is between sunrise/set
def check_between_sunset_rise(log, weather_current):

    # Get current weather
    weather_status, datas = get_check_current_weather(log, weather_current)
    if weather_status:

        # Check API attr
        if 'sys' in datas and 'sunset' in datas['sys'] and 'sunrise' in datas['sys']:
            sunset_time = datetime.datetime.fromtimestamp(int(datas['sys']['sunset']))
            sunrise_time = datetime.datetime.fromtimestamp(int(datas['sys']['sunrise']))

            # Check if it's today sunset
            now = datetime.datetime.now()
            if sunset_time.date() == now.date():

                # Check if current are between sunset/rise
                if sunrise_time < now < sunset_time:
                    return True
    return False


# Check is rain (it check even not heavy rain)
def check_rain(log, weather_current):

    # Get current weather
    weather_status, datas = get_check_current_weather(log, weather_current)
    if weather_status:

        # Check API attr
        if 'weather' in datas:
            if len(datas['weather']) > 0:
                if 'id' in datas['weather'][0]:
                    return is_raining_drizzle(str(datas['weather'][0]['id']))
        log.log_error(f"In function (check_rain), API attr error")
    return False


# Check if a lot of cloud in the sky
# If True => means we cannot see the sun
def check_cloud(log, weather_current):

    # Get current weather
    weather_status, datas = get_check_current_weather(log, weather_current)
    if weather_status:

        # Check API attr
        if 'weather' in datas:
            if len(datas['weather']) > 0:
                if 'id' in datas['weather'][0]:
                    return is_cloudy(str(datas['weather'][0]['id']))
                log.log_error(f"In function (check_rain), API attr error")
    return False


# Get current temp from API/DB and check if well formatted
def get_current_external_temp(log, weather_current):

    # Get current weather
    weather_status, datas = get_check_current_weather(log, weather_current)
    if weather_status:
        try:
            if "main" in datas and "temp" in datas["main"]:
                value = get_degree_from_kelvin(float(datas['main']['temp']))
                return True, value
            else:
                log.log_error(f"In function (get_current_external_temp), API/DB label error")
        except ValueError:
            log.log_error(f"In function (get_current_external_temp), the temp given by the API/DB is not float")
    return False, None


# Check heat period
# True => heater on
# False => heater off
def check_heat_period(automation_rule):
    now = datetime.datetime.now()
    start_day = automation_rule.heater_on_start_day
    start_month = automation_rule.heater_on_start_month
    stop_day = automation_rule.heater_on_stop_day
    stop_month = automation_rule.heater_on_stop_month

    # Check if now is during the heat period or not
    if now.day <= start_day and now.month <= start_month and now.day >= stop_day and now.month >= stop_month:
        return True
    return False