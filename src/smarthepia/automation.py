import time as time_sleep

from ephem import hours
from pysolar.solar import *
import datetime
import statistics
import sys
import os

# MongoDB driver
import pymongo
from pymongo.errors import ConnectionFailure

# Local import
import const
import utils
import datastruct
import logger
import conf
import weather
import sun
import heater
from simple_pid import PID

DEBUG = 1

class Automation(object):
    def __init__(self):
        self.__client = None
        self.rooms = []
        self.automation_rule = None
        self.season = None
        self.automation_log = None
        self.weather_forecast = None
        self.weather_current = None
        #self.pids = []
        self.pids = None

    def run(self):

        # Check if log are well init
        if self.log_init():

            self.pids = heater.Heater()

            # self.close_one_blind("192.168.1.137", "5000", "4/2")

            # For first start tempo
            # time.sleep(const.st_start)

            # Process automation
            while True :
                print("Automation")

                # Init MongoDB client
                status, self.__client = self.db_connect()

                if status:

                    # Start to automation
                    self.process_automation()

                    # Clear room otherwise add many
                    self.rooms.clear()

                    # Close db
                    self.__client.close()

                # Sleep until next time
                time_sleep.sleep(const.st_automation)

    # Init log
    def log_init(self):

        ldp_status , log_dir_path = conf.get_log_dir_path()
        len_status, log_ext_name = conf.get_log_ext_name()
        lfms_status, log_file_max_size = conf.get_log_file_max_size()
        if ldp_status and len_status and lfms_status:
            sp_name = str(os.path.basename(__file__)).replace(".py", "")
            self.automation_log = logger.Logger(str(log_dir_path), int(log_file_max_size), sp_name, str(log_ext_name))
            self.automation_log.log_info(f"Subprocess {sp_name} started")
            return True
        else:
            return False

    # Connect to the database
    def db_connect(self):
        try:
            return True, pymongo.MongoClient(const.db_host, const.db_port)
        except pymongo.errors.ConnectionFailure as e:
            return False, None

    def get_automation_rule(self):
        datas = self.__client.sh.automations.find_one()
        self.automation_rule = datastruct.StructAutomationRule(datas['hpstartday'], datas['hpstartmonth'], datas['hpstopday'], datas['hpstopmonth'], datas['hptempmin'], datas['hptempmax'], datas['nhptempmin'], datas['nhptempmax'], datas['outtempmin'], datas['outsummax'], datas['kp'],datas['ki'],datas['kd'])
        i = 0

    # Start to automation
    def process_automation(self):

        # Get season of today
        self.season = sun.get_season(datetime.date.today())

        # Get all info (sensor, actuator, rule) by room
        self.get_room()

        # Get automation rule
        self.get_automation_rule()

        # Get last weather measures and forecast
        self.weather_forecast = self.get_forecast(True)
        self.weather_current = self.get_current_weather(True)

        # Check if we have room to process automation
        if len(self.rooms) > 0:

            # Walk through all room
            for room in self.rooms:

                # Process blind rule
                self.process_blinds(room)

                # If True => we can process the room
                multisensor_status, temp, measures = self.check_multisensor(room.sensors)
                if multisensor_status:

                    # Process valve rule
                    self.process_valves(room, temp)

    # Get all rooms
    # Not disabled & not in error
    def get_room(self):
        query = {'$and': [{"type": const.db_devices_type_room}, {"enable": True}, {'$or': [{'itemStyle.color': {'$eq': const.device_color_no_error}}, {'itemStyle.color': {'$eq': const.device_color_warning}}]}]}
        datas = self.__client.sh.devices.find(query)
        print(datas.count())
        for data in datas:

            # If we have sensor available add room to check
            # Otherwise we dont check the room cause no sensor to give info about motion.
            # Also check if actuator are available
            # Cause if not available we can't do any automation.
            # If rule automation by room is disable => no automation.
            sensor_status, sensors = self.get_sensor_by_room(data['id'])
            actuator_status, actuators = self.get_actuator_by_room(data['id'])
            rule = self.get_rules_by_room(data['rules'])
            room_id = str(data['_id'])
            if sensor_status and actuator_status and rule['active']:
                self.rooms.append(datastruct.StructAutomation(sensors, actuators, rule, data['orientation'], room_id))

    # Get rule ba room
    def get_rules_by_room(self, room_rule):
        query = {"name": room_rule}
        return self.__client.sh.rules.find_one(query)

    # Get sensors by room id
    def get_sensor_by_room(self, room_id):
        sensors = []
        #query = {'$and': [{"parent": int(room_id)}, {'type': {'$nin': const.db_devices_type_not_location_actuator}}]}
        query = {'$and': [{"parent": int(room_id)},{'subtype': const.db_devices_sub_type_multisensor}]}
        datas = self.__client.sh.devices.find(query)

        # Check if sensor available
        if datas.count() != 0:
            for data in datas:
                sensors.append(data)
            return True, sensors
        else:
            return False, None

    # Get actuators by room id
    def get_actuator_by_room(self, room_id):
        actuators = []
        #query = {'$and': [{"parent": int(room_id)}, {'type': {'$nin': const.db_devices_type_not_location_sensor}}, {}]}
        query = {'$and': [{"parent": int(room_id)}, {'subtype': {'$in': const.db_devices_sub_type_actuator}}]}
        datas = self.__client.sh.devices.find(query)

        # Check if actuator available
        if datas.count() != 0:
            for data in datas:
                actuators.append(data)
            return True, actuators
        else:
            return False, None

    # Get measure by multisensor
    def get_measure_by_multisensor(self, dependency_name, address):
        query = {'$and': [{'depname': dependency_name}, {'devices.method': {'$eq': const.dependency_device_type_rest}}]}
        devices = self.__client.sh.dependencies.find_one(query)

        # Get REST server ip and port
        ip = ""
        port = 0
        for device in devices['devices']:
            if device['method'] == const.dependency_device_type_rest:
                ip = device['ip']
                port = device['port']

        # Get measures by multisensor
        status, datas = utils.get_mesures(const.route_zwave_device_all_measures(ip, str(port), address))
        if status:
            return True, datas
        self.automation_log.log_error(f"In function (get_measure_by_multisensor), the multisensor measure could not be given")
        return False, None

    # Get last forecast from api or db if fail
    def get_forecast(self, local):

        # Get last forecast from db
        # TODO remove after
        if not local:

            # If error we get last data from db
            status, api_datas = weather.get_api_forecast()
            if status:
                self.__client.sh.apiforecast.insert(api_datas)
                return api_datas
            else:
                self.automation_log.log_error(f"In function (get_forecast), API measure available")
                return self.get_db_forecast()
        else:
            return self.get_db_forecast()

    # Get last current weather from api or db if fail
    def get_current_weather(self, local):

        # Get last measures from db
        db_datas = self.get_db_current_weather()

        # Get last measures from db
        # TODO remove after
        if not local:

            # Get last measures from api
            status, api_datas = weather.get_api_current_weather()

            # If get measures from api
            if status:

                # If the api have a new measures then we add it to the db and return it
                # Else give last measure from db
                if datetime.datetime.fromtimestamp(int(db_datas['dt'])) < datetime.datetime.fromtimestamp(int(api_datas['dt'])):
                    self.__client.sh.apicurrents.insert(api_datas)
                    return api_datas
                else:
                    return db_datas
            else:
                self.automation_log.log_error(f"In function (get_current_weather), API measure available")
                return db_datas
        else:
            return db_datas

    # Get last current weather measure from db
    def get_db_current_weather(self):
        return self.__client.sh.apicurrents.find_one({'$query': {}, '$orderby': {'$natural': -1}})

    # Get last forecast measure from db
    def get_db_forecast(self):
        return self.__client.sh.apiforecast.find_one({'$query': {}, '$orderby': {'$natural': -1}})

    # Check all the multisenor for one room
    def check_motion_all_multisensors_in_room(self, sensors):

        # Get all multisensor and get dependency name and address
        # to check if motion is recorded
        motion = False
        for sensor in sensors:
            motion_status = self.check_multisensor_motion(sensor['dependency'], sensor['address'])

            # Check if the motion status is not
            # 0 => Nobody in the room
            # 1 => Someone on the room
            # -1 => Multisensor error or date not up to date
            if motion_status == 1 or motion_status == -1:
                motion = True
        return motion

    # Get last 4 motion measure to check if no one is in the room
    def check_multisensor_motion(self, dependency, address):

        # Date diff to compare the 4 measures up date time
        diff = datetime.datetime.now() - datetime.timedelta(minutes=25)

        # Get last 4 measure (sorted by _id)
        datas = self.__client.sh.stats.find({'$and': [{"dependency": dependency}, {"address": str(address)}]}).sort([("_id", -1)]).limit(4)

        # Return - if not enough data
        # Or dependency name not fount
        # Or address not fount
        if datas.count() > 4:
            for data in datas:

                # Return -1 if one of the last timestamp if not up to date
                # Last 4 measures cannot be taken if => not up to date
                if data['updatetime'] < diff:
                    return -1
                if data['motion']:
                    return 1

        else:
            return -1
        return 0

    def check_multisensor_time(self, updatetime):

        # Check if the last multisensor measure (temp)
        # are up to date. We check multisensor every 5 min so let say that 6 min is enough
        # To say if the multisensor is up to date
        diff = datetime.datetime.now() - datetime.timedelta(minutes=6)
        measure_update_time = datetime.datetime.fromtimestamp(int(updatetime))

        # Check if the diff is smaller then the current temp
        if diff < measure_update_time:
            return True
        else:
            self.automation_log.log_error(f"In function (check_multisensor_time), the multisensor is not up to date")
            return False

    # Process automation room by room
    def check_multisensor(self, sensors):

        measures = []
        for sensor in sensors:

            # Get measure by multisensor (http get)
            # Check if response
            measure_status, measure = self.get_measure_by_multisensor(sensor['dependency'], sensor['address'])
            if measure_status:

                # Check multisensor timestamp
                # If False => multisensor no uptodate
                time_status = self.check_multisensor_time(measure['updateTime'])
                if time_status:
                    measures.append(measure)

        if len(measures) > 0:
            status, temp = self.check_multisensor_temp(measures)
            if status:
                return True, temp, measures
        return False, None, None

    # Check if sensors temperature value is enough good
    # To rely on it
    def check_multisensor_temp(self, measures):

        # If sensor temp value if heigher or lower then max and min threshold
        status, sensors_td = self.check_threshold_temp(measures)

        # Check if we have at least one sensor ok with threshold
        if status:
            if len(sensors_td) == 1:

                # Return first value
                return True, next(iter(sensors_td))
            elif len(sensors_td) >= 2:

                # Check if at least 2 sensor have the same temp
                return True, self.check_temp_correl(sensors_td)
            else:
                self.automation_log.log_error(f"In function (check_multisensor_temp), no sensor available to give temp")
                return False, None
        else:
            return False, None

    # Check min and max threshold to det if sensor value error
    def check_threshold_temp(self, measures):

        # Check if heating period
        hp = self.check_heat_period()
        sensor_th_check = []
        for measure in measures:

            # If we are in heating period => take other threshold
            if hp:
                min = self.automation_rule.heater_on_temp_min
                max = self.automation_rule.heater_on_temp_max
            else:
                min = self.automation_rule.heater_off_temp_min
                max = self.automation_rule.heater_off_temp_max

            # Check min and max threshold
            if min < measure['temperature'] < max:
                sensor_th_check.append(measure['temperature'])

        if len(sensor_th_check) > 0:
            return True, sensor_th_check
        self.automation_log.log_error(f"In function (check_threshold_temp), the min or max threshold passed")
        return False, None

    # Correlation between all sensor
    def check_temp_correl(self, sensor_th_check):

        # Get temp median between all sensor temp value
        return statistics.median(sensor_th_check)

    # Check heat period
    # True => heater on
    # False => heater off
    def check_heat_period(self):
        now = datetime.datetime.now()
        start_day = self.automation_rule.heater_on_start_day
        start_month = self.automation_rule.heater_on_start_month
        stop_day = self.automation_rule.heater_on_stop_day
        stop_month = self.automation_rule.heater_on_stop_month

        # Check if now is during the heat period or not
        if now.day <= start_day and now.month <= start_month and now.day >= stop_day and now.month >= stop_month:
            return True
        return False

    # Process rule about valves
    def process_valves(self, room, temp):

        self.get_pid_by_room(room, 24)

        # Check if head period
        hp = self.check_heat_period()

        if hp:
            pass

        else:
            pass

    # Process rule about blinds
    def process_blinds(self, room):

        # If it's night time => close blind
        # Else => process day time rule by room
        night_time_status = self.check_night_time(room.rule['dt'], room.rule['nt'])
        if night_time_status:
            if DEBUG: print(f"Night time")

            # Get blind night rule
            # If 1 => Off
            # If 2 => On
            if room.rule['bnr'] == const.night_blind_on:
                self.close_all_blinds(room.actuators)
        else:
            if DEBUG: print(f"Day time")

            # Check if all multisensor dont return false
            # True => Someone in the room or (multisensor error/not up to date)
            # False => Nobody in the room
            motion_status = self.check_motion_all_multisensors_in_room(room.sensors)
            if not motion_status:

                # Check if the sun is not visible at all or not
                sunrise_sunset = self.check_between_sunset_rise()
                is_cloudy = self.check_cloud()

                # Get what to do with th blind during day time
                # Get room rule
                if room.rule['bdr'] != const.day_blind_off:  # not Off

                    if room.rule['bdr'] == const.day_blind_sam:  # Sun and no motion => blind down
                        status = self.rule_sun_and_no_motion(room, sunrise_sunset, is_cloudy)
                        if status:
                            if DEBUG: print(f"Sun and !motion => blind down")
                            self.close_all_blinds(room.actuators)
                    elif room.rule['bdr'] == const.day_blind_ram:  # Rain and no motion => blind down

                        # Close all blind if rain
                        if self.check_rain():
                            self.close_all_blinds(room.actuators)
                    elif room.rule['bdr'] == const.day_blind_full: # Rain and no motion and Sun and no motion => blind down

                        # Close all blind if rain
                        # Else check if sun in the room
                        if self.check_rain():
                            self.close_all_blinds(room.actuators)
                        else:
                            status = self.rule_sun_and_no_motion(room, sunrise_sunset, is_cloudy)
                            if status:
                                if DEBUG: print(f"Sun and !motion => blind down")
                                self.close_all_blinds(room.actuators)

                    else:
                        self.automation_log.log_info(f"In function (process_blinds), the rule ({str(room.rule['bdr'])}) is not implemented")
                        if DEBUG: print(f"Day time rule not implemented")

    # Check if we are in night time => close all blinds
    def check_night_time(self, rule_day_time, rule_night_time):

        # Get current date and convert day and night time to time()
        time_now = datetime.datetime.now().time()
        night_time = datetime.datetime.strptime(f"{rule_night_time}:00", '%H:%M:%S').time()
        day_time = datetime.datetime.strptime(f"{rule_day_time}:00", '%H:%M:%S').time()

        before_midnight = datetime.datetime.strptime(f"23:59:59", '%H:%M:%S').time()
        midnight = datetime.datetime.strptime(f"00:00:00", '%H:%M:%S').time()
        after_midnight = datetime.datetime.strptime(f"00:00:01", '%H:%M:%S').time()

        # Sleep 1 sec if 00:00:00
        if time_now == midnight:
            time_sleep.sleep(1)

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

    # Process closing all blind
    def close_all_blinds(self, actuators):

        # Get all actuator by room
        for actuator in actuators:

            # Check if blind
            if actuator['subtype'] == const.db_devices_sub_type_blind:

                # Get ip and port for this actuator
                actuator_status, ip, port = self.get_knx_network_by_device(actuator['dependency'])
                if actuator_status:
                    self.close_one_blind(ip, port, actuator['address'])

    # Close one blind
    def close_one_blind(self, ip, port, address):

        # Check if the blind is not already at max => 255
        # Prevent blind forcing
        blind_read_status, value = self.get_blind_value(ip, port, address)
        if blind_read_status:
            if value != const.blind_max_value:

                # Gen knx route to close blind => 255
                route_status, write_route = const.route_knx_device_value_write(ip, port, address, const.db_devices_sub_type_blind, const.blind_max_value)
                if route_status:
                    status, result = utils.http_get_request_json(write_route)
                    if not status:
                        # TODO error (maybe alarm) if we cant do it after 20min
                        # Global var list of error blind
                        self.automation_log.log_error(f"In function (close_one_blind), cannot write {const.blind_max_value} to blind")

    # Get value (read) from blind
    def get_blind_value(self, ip, port, address):

        # Check if the blind is not already at max => 255
        # Prevent blind forcing
        read_route = const.route_knx_device_value_read(ip, port, address, const.db_devices_sub_type_blind)
        status, result = utils.http_get_request_json(read_route)
        if not status:
            self.automation_log.log_error(f"In function (close_one_blind), cannot read value from blind")
        else:

            # Check is result label exist
            if "status" in result and "result" in result:
                try:

                    # Parse value to int and check if between 0 and 255
                    value = int(result['result'])
                    if const.blind_min_value <= value <= const.blind_max_value:
                        return True, value
                    else:
                        self.automation_log.log_error(f"In function (get_blind_value), the bind value is not between 0 and 255")
                except ValueError:
                    self.automation_log.log_error(f"In function (get_blind_value), the bind value is not an int")
            else:
                self.automation_log.log_error(f"In function (get_blind_value), result label are not well formatted")
        return False, None


    # Get knx dependency device type REST
    # => ip and port
    def get_knx_network_by_device(self, dependency_device_name):

        # Get dependency
        query = {'$and': [{'depname': dependency_device_name}, {'devices.method': {'$eq': const.dependency_device_type_rest}}]}
        devices = self.__client.sh.dependencies.find_one(query)

        # Get REST server ip and port
        ip = ""
        port = 0
        for device in devices['devices']:
            if device['method'] == const.dependency_device_type_rest:
                ip = device['ip']
                port = device['port']

        # Check if ip and port not empty
        # => Can be an error if not ip and port
        if ip == "" or port == 0:
            return False, None, None
        return True, ip, port

    # Check if the curretn weather from DB/API are good
    def get_check_current_weather(self):

        # Check if data have been setted
        if self.weather_current is not None:

            # Get current weather
            datas = self.weather_current
            if 'dt' in datas:

                # Check if Weather API/DB return good value
                now_diff = datetime.datetime.now() - datetime.timedelta(hours=4)
                if datetime.datetime.fromtimestamp(int(datas['dt'])) > now_diff:
                    return True, datas
                else:
                    self.automation_log.log_error(f"In function (get_check_current_weather) weather API/DB return bad updated value")
                    return False, None
            else:
                self.automation_log.log_error(f"In function (get_check_current_weather) weather data error")
                return False, None
        else:
            self.automation_log.log_error(f"In function (get_check_current_weather) weather data are None")
            return False, None

    # Check if current time is between sunrise/set
    def check_between_sunset_rise(self):

        # Get current weather
        weather_status, datas = self.get_check_current_weather()
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
    def check_rain(self):

        # Get current weather
        weather_status, datas = self.get_check_current_weather()
        if weather_status:

            # Check API attr
            if 'weather' in datas:
                if len(datas['weather']) > 0:
                    if 'id' in datas['weather'][0]:
                        return weather.is_raining_drizzle(str(datas['weather'][0]['id']))
            self.automation_log.log_error(f"In function (check_rain), API attr error")
        return False

    # Check if a lot of cloud in the sky
    # If True => means we cannot see the sun
    def check_cloud(self):

        # Get current weather
        weather_status, datas = self.get_check_current_weather()
        if weather_status:

            # Check API attr
            if 'weather' in datas:
                if len(datas['weather']) > 0:
                    if 'id' in datas['weather'][0]:
                        return weather.is_cloudy(str(datas['weather'][0]['id']))
            self.automation_log.log_error(f"In function (check_rain), API attr error")
        return False

    # Get current temp from API/DB and check if well formatted
    def get_current_external_temp(self):

        # Get current weather
        weather_status, datas = self.get_check_current_weather()
        if weather_status:
            try:
                if "main" in datas and "temp" in datas["main"]:
                    value = weather.get_degree_from_kelvin(float(datas['main']['temp']))
                    return True, value
                else:
                    self.automation_log.log_error(f"In function (get_current_external_temp), API/DB label error")
            except ValueError:
                self.automation_log.log_error(f"In function (get_current_external_temp), the temp given by the API/DB is not float")
        return False, None

    # Rule to close blind when sun and no motion
    # In addition we add if hot season and height temp
    def rule_sun_and_no_motion(self, room, sunrise_sunset, is_cloudy):

        # Check if sun anyway
        if sunrise_sunset:

            # If cloud => no sun
            if not is_cloudy:

                # Check if sun in the room
                is_sun, error = sun.is_sun_in_room(room.orientation)
                if error != -1:
                    if is_sun:
                        # During spring and summer the temp can reach height temps
                        if self.season == sun.season_summer or self.season == sun.season_spring:

                            # Get current external temp
                            temp_status, current_external_temp = self.get_current_external_temp()
                            if temp_status:

                                # Check if outside temp is height (base => 25)
                                if current_external_temp >= self.automation_rule.out_temp_sum_max:
                                    return True
                            else:
                                self.automation_log.log_error(f"In function (rule_sun_and_no_motion), the external temp could not be found")
                else:
                    self.automation_log.log_error(f"In function (process_blinds), the room orientation is not valid")
        return False

    # Get =>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def get_pid_by_room(self, room, indoor_temp):

        # Get all rooms which contains valves
        # The class heater will delete (pid) if not in list
        room_ids = self.get_all_rooms()

        # Get consign temp rule
        rule_temp = int(room.rule['temp'])

        value_status, value, p = self.pids.get_computed_value(room.room_id, room_ids, indoor_temp, rule_temp, self.automation_rule.kp, self.automation_rule.ki, self.automation_rule.kd)
        print(f"room id:{room.room_id} pid:{id(p)} value:{value}")

        if value_status:
            pass
        else:
            self.automation_log.log_error(f"In function (set_valve), pid by room ({room.room_id}) is not found")

    # Get all rooms which contains valves
    # Return all the room ids
    def get_all_rooms(self):

        room_ids = []
        # Get all rooms
        query = {"type": const.db_devices_type_room}
        datas = self.__client.sh.devices.find(query)
        for data in datas:
            room_id = data['_id']

            # Check if valve in this room
            is_valve = self.get_valve_by_room(data['id'])
            if is_valve:

                # Add room id which contain valve
                room_ids.append(str(room_id))
        return room_ids

    # Get actuators by room id
    def get_valve_by_room(self, room_id):
        query = {'$and': [{"parent": int(room_id)}, {'subtype': const.db_devices_sub_type_valve}]}
        datas = self.__client.sh.devices.find(query)

        # Check if there is valve
        if datas.count() != 0:
            return True
        else:
            return False





