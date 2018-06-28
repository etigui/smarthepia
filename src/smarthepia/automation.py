import time
from pysolar.solar import *
import datetime
import statistics
import sys

# MongoDB driver
import pymongo
from pymongo.errors import ConnectionFailure

# Local import
import const
import utils
import datastruct

DEBUG = 1


class Automation(object):
    def __init__(self):
        self.__client = None
        self.rooms = []
        self.automation_rule = None
        self.season = None

    def run(self):

        # For first start tempo
        #time.sleep(const.st_start)

        # Process automation
        while True :
            print("Automation")

            # Init MongoDB client
            status, self.__client = self.db_connect()

            if status:

                # Start to automation
                self.process_automation()

                # Close db
                self.__client.close()

            # Sleep until next time
            time.sleep(const.st_automation)


    # Connect to the database
    def db_connect(self):
        try:
            return True, pymongo.MongoClient(const.db_host, const.db_port)
        except pymongo.errors.ConnectionFailure as e:
            return False, None

    def get_automation_rule(self):
        datas = self.__client.sh.automations.find_one()
        self.automation_rule = datastruct.StructAutomationRule(datas['hpstartday'], datas['hpstartmonth'], datas['hpstopday'], datas['hpstopmonth'], datas['hptempmin'], datas['hptempmax'], datas['nhptempmin'], datas['nhptempmax'], datas['outtempmin'])
        i = 0

    # Start to automation
    def process_automation(self):

        # Get season of today
        self.season = utils.get_season(datetime.date.today())

        # Get all info (sensor, actuator, rule) by room
        self.get_room()

        # Get automation rule
        self.get_automation_rule()

        # Get last weather measures and forecast
        api_forecast = self.get_api_forecast(True)
        api_current = self.get_api_current_weather(True)

        # Check if we have room to process automation
        if len(self.rooms) > 0:

            # Walk through all room
            for room in self.rooms:

                # If True => we can process the room
                status, temp, measures = self.check_multisensor(room.sensors)
                if status:

                    # Check if all multisensor dont return false
                    # True => Someone in the room or (multisensor error/not up to date)
                    # False => Nobody in the room
                    motion_status = self.check_motion_all_multisensors_in_room(room.sensors)
                    if motion_status:
                        self.process_blinds(room)

                self.process_valves()
            i = 0

    # Get all rooms
    # Not disabled & not in error
    def get_room(self):
        query = {'$and': [{"type": const.db_devices_type_room}, {"enable": True}, {'$or': [{'itemStyle.color': {'$eq': const.device_color_no_error}}, {'itemStyle.color': {'$eq': const.device_color_warning}}]}]}
        datas = self.__client.sh.devices.find(query)
        for data in datas:

            # If we have sensor available add room to check
            # Otherwise we dont check the room cause no sensor to give info about motion.
            # Also check if actuator are available
            # Cause if not available we can't do any automation.
            # If rule automation by room is disable => no automation.
            sensor_status, sensors = self.get_sensor_by_room(data['id'])
            actuator_status, actuators = self.get_actuator_by_room(data['id'])
            rule = self.get_rules_by_room(data['rules'])
            if sensor_status and actuator_status and rule['active']:
                self.rooms.append(datastruct.StructAutomation(sensors, actuators, rule, data['orientation']))

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
        return False, None

    # Get last forecast from api or db if fail
    def get_api_forecast(self, local):

        # Get last forecast from db
        # TODO remove after
        if not local:

            # If error we get last data from db
            status, api_datas = utils.get_forecast()
            if status:
                self.__client.sh.apiforecast.insert(api_datas)
                return api_datas
            else:
                return self.get_db_forecast()
        else:
            return self.get_db_forecast()

    # Get last current weather from api or db if fail
    def get_api_current_weather(self, local):

        # Get last measures from db
        db_datas = self.get_db_current_weather()

        # Get last measures from db
        # TODO remove after
        if not local:

            # Get last measures from api
            status, api_datas = utils.get_current_weather()

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
    # Get last 2 motion measure to check if no one is in the room
    def check_multisensor_motion(self, dependency, address):

        # Date diff to compare the 2 measures up date time
        diff = datetime.datetime.now() - datetime.timedelta(minutes=15)

        # Get last 2 measure (sorted by _id)
        datas = self.__client.sh.stats.find({'$and': [{"dependency": dependency}, {"address": str(address)}]}).sort([("_id", -1)]).limit(2)

        # Return - if not enough data
        # Or dependency name not fount
        # Or address not fount
        if datas.count() > 2:
            for data in datas:

                # Return -1 if one of the last timestamp if not up to date
                # Last 2 measures cannot be taken if => not up to date
                if data['updatetime'] < diff:
                    return -1
                if data['motion']:
                    return 1

        else:
            return -1
        return 0

    def check_multisensor_time(self, updatetime):
        return True

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

    # Process rule about blinds
    def process_blinds(self, room):

        # If it's night time => close blind
        # Else => process day time rule by room
        night_time_status = self.check_night_time(room.rule['dt'], room.rule['nt'])
        if not night_time_status:
            if DEBUG: print(f"Night time")
            self.process_night_time(room.actuators)
        else:
            if DEBUG: print(f"Day time")

    # Check if we are in night time => close all blinds
    def check_night_time(self, rule_day_time, rule_night_time):

        # Get current date and convert day and night time to time()
        time_now = datetime.datetime.now().time()
        night_time = datetime.datetime.strptime(f"{rule_night_time}:00", '%H:%M:%S').time()
        day_time = datetime.datetime.strptime(f"{rule_day_time}:00", '%H:%M:%S').time()

        # If we are during the night period
        # Between => eg: 23:00:00 => 08:00:00
        if night_time < time_now < day_time:
            return True
        return False

    # Process closing all blind
    def process_night_time(self, actuators):

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

        # Gen knx route to close blind => 255
        route_status, route = const.route_knx_device_value_write(ip, port, address, const.db_devices_sub_type_blind, const.blind_max_value)
        if route_status:
            status, result = utils.http_get_request_json(route)
            if not status:
                # TODO error (maybe alarm) if we cant do it after 20min
                # Global var list of error blind
                if DEBUG: print(f"Cannot write {const.blind_max_value} to blind")

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

    # Process rule about valves
    def process_valves(self):
        pass
