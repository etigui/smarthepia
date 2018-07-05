import time
import datetime
import statistics
import sys
import os
import psutil

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
import valve
import blind
import multisensor


class Automation(object):
    def __init__(self):
        self.__client = None
        self.rooms = []
        self.automation_rule = None
        self.season = None
        self.automation_log = None
        self.weather_forecast = None
        self.weather_current = None
        self.pids = None
        self.night_dismissed = False

    def run(self):

        # For first start tempo
        #time.sleep(const.st_start)

        # Check if log are well init
        if self.log_init():

            self.pids = heater.Heater()

            # Process automation
            while True :
                if const.DEBUG: print(f"Automation process: {datetime.datetime.now()}")

                # Init MongoDB client
                status, self.__client = self.db_connect()

                if status:

                    # Start to automation
                    self.process_automation()

                    # Clear room otherwise add many
                    self.rooms.clear()

                    # Close db
                    self.__client.close()
                else:
                    self.automation_log.log_error(f"In function (run), could not connect to the db")

                # Wait new iter
                time.sleep(const.st_automation)

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
            client = pymongo.MongoClient(const.db_host, const.db_port, serverSelectionTimeoutMS=1)
            client.server_info()
            if client is not None:
                return True, client
            else:
                return False, None
        except pymongo.errors.ConnectionFailure as e:
            return False, None

    # Start to automation
    def process_automation(self):

        # Get season of today
        self.season = sun.get_season(datetime.date.today())

        # Get all info (sensor, actuator, rule) by room
        self.get_room()

        # Get automation rule
        self.get_automation_rule()

        # Get last weather measures and forecast
        self.weather_forecast = weather.get_forecast(self.__client, self.automation_log, True)
        self.weather_current = weather.get_current_weather(self.__client, self.automation_log, True)

        # Check if we have room to process automation
        if len(self.rooms) > 0:

            # Walk through all room
            for room in self.rooms:

                # Process blind rule
                self.process_blinds(room)

                # If True => we can process the room
                #multisensor_status, temp, measures = multisensor.check_multisensor(self.__client, self.automation_log, self.automation_rule, room.sensors)
                #if multisensor_status:

                    # Process valve rule
                    #self.process_valves(room, temp)
                self.process_valves(room, 26)

    # Get automation rule
    def get_automation_rule(self):
        datas = self.__client.sh.automations.find_one()
        self.automation_rule = datastruct.StructAutomationRule(datas['hpstartday'], datas['hpstartmonth'], datas['hpstopday'], datas['hpstopmonth'], datas['hptempmin'], datas['hptempmax'], datas['nhptempmin'], datas['nhptempmax'], datas['outsummax'], datas['kp'],datas['ki'],datas['kd'], datas['outtempmin'], datas['intempmin'])

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
            sensor_status, sensors = multisensor.get_multisensor_by_room(self.__client, data['id'])
            actuator_status, actuators = self.get_actuator_by_room(data['id'])
            rule = self.get_rules_by_room(data['rules'])
            room_id = str(data['_id'])
            if sensor_status and actuator_status and rule['active']:
                self.rooms.append(datastruct.StructAutomation(sensors, actuators, rule, data['orientation'], room_id))

    # Get rule ba room
    def get_rules_by_room(self, room_rule):
        query = {"name": room_rule}
        return self.__client.sh.rules.find_one(query)

    # Get actuators by room id
    def get_actuator_by_room(self, room_id):
        try:
            actuators = []
            query = {'$and': [{"parent": int(room_id)}, {'subtype': {'$in': const.db_devices_sub_type_actuator}}]}
            datas = self.__client.sh.devices.find(query)

            # Check if actuator available
            if datas.count() != 0:
                for data in datas:
                    actuators.append(data)
                return True, actuators
            else:
                return False, None
        except Exception as e:
            self.automation_log.log_info(f"In function (get_actuator_by_room), room id might not be an string with number")
            return False, None

    # Process rule about valves
    def process_valves(self, room, indoor_temp):

        # Get valve day/night rule
        # If 1 => Off
        # If 2 => On
        if room.rule['vdnr'] == const.daynight_valve_on:

            # Check if head period
            hp = weather.check_heat_period(self.automation_rule)
            if hp:

                # Get pid value for the current room to set to valve
                valve.set_all_valves(self.pids, self.__client, self.automation_log, self.automation_rule, room, indoor_temp)
            else:

                # Get current external temp
                temp_status, current_external_temp = weather.get_current_external_temp(self.automation_log, self.weather_current)
                if temp_status:

                    # If outdoor temp is low same as indoor we can open the valve
                    if indoor_temp <= self.automation_rule.in_temp_min and self.automation_rule.out_temp_min <= current_external_temp:

                        # Get pid value for the current room to set to valve
                        valve.set_all_valves(self.pids, self.__client, self.automation_log, self.automation_rule, room,indoor_temp)
                else:
                    self.automation_log.log_error(f"In function (process_valves), the temp given by the API/DB is not available")

    # Process rule about blinds
    def process_blinds(self, room):

        # If it's night time => close blind
        # Else => process day time rule by room
        night_time_status = weather.check_night_time(room.rule['dt'], room.rule['nt'])
        if not night_time_status:

            # Close only one time the blind
            # At day time the value will be setted to False again
            if not self.night_dismissed:
                if const.DEBUG: print(f"Night time")
                self.night_dismissed = True

                # Get blind night rule
                # If 1 => Off
                # If 2 => On
                if room.rule['bnr'] == const.night_blind_on:
                    blind.close_all_blinds(self.automation_log, self.__client, room.actuators)
            else:
                if const.DEBUG: print(f"Night time dismissed")
        else:
            if const.DEBUG: print(f"Day time")
            night_dismissed = False

            # Check if all multisensor dont return false
            # True => Someone in the room or (multisensor error/not up to date)
            # False => Nobody in the room
            motion_status = multisensor.check_motion_all_multisensors_in_room(self.__client, room.sensors)
            if not motion_status:

                # Check if the sun is not visible at all or not
                sunrise_sunset = weather.check_between_sunset_rise(self.automation_log, self.weather_current)
                is_cloudy = weather.check_cloud(self.automation_log, self.weather_current)

                # Get what to do with th blind during day time
                # Get room rule
                if room.rule['bdr'] != const.day_blind_off:  # not Off

                    if room.rule['bdr'] == const.day_blind_sam:  # Sun and no motion => blind down
                        status = blind.rule_sun_and_no_motion(self.season, self.automation_rule, self.automation_log, self.weather_current, room, sunrise_sunset, is_cloudy)
                        if status:
                            if const.DEBUG: print(f"Sun and !motion => blind down")
                            blind.close_all_blinds(self.automation_log, self.__client, room.actuators)
                    elif room.rule['bdr'] == const.day_blind_ram:  # Rain and no motion => blind down

                        # Close all blind if rain
                        if weather.check_rain(self.automation_log, self.weather_current):
                            blind.close_all_blinds(self.automation_log, self.__client, room.actuators)
                    elif room.rule['bdr'] == const.day_blind_full: # Rain and no motion and Sun and no motion => blind down

                        # Close all blind if rain
                        # Else check if sun in the room
                        if weather.check_rain(self.automation_log, self.weather_current):
                            blind.close_all_blinds(self.automation_log, self.__client, room.actuators)
                        else:
                            status = blind.rule_sun_and_no_motion(self.season, self.automation_rule, self.automation_log, self.weather_current, room, sunrise_sunset, is_cloudy)
                            if status:
                                if const.DEBUG: print(f"Sun and !motion => blind down")
                                blind.close_all_blinds(self.automation_log, self.__client, room.actuators)

                    else:
                        self.automation_log.log_info(f"In function (process_blinds), the rule ({str(room.rule['bdr'])}) is not implemented")
                        if const.DEBUG: print(f"Day time rule not implemented")

