import time
from pysolar.solar import *
import datetime

# MongoDB driver
import pymongo
from pymongo.errors import ConnectionFailure

# Local import
import const
import utils
import datastruct


class Automation(object):
    def __init__(self):
        self.__client = None
        self.automations = []

    def run(self):

        # For first start tempo
        #time.sleep(const.st_start)

        # Process automation
        while True :
            print("Automation")

            # Init MongoDB client
            status, self.__client = self.db_connect()

            print(utils.get_season(datetime.date.today()))

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

    # Start to automation
    def process_automation(self):

        # Get all info (sensor, actuator, rule) by room
        self.get_room()

        # Get last weather measures and forecast
        api_forecast = self.get_api_forecast(True)
        api_current = self.get_api_current_weather(True)

        # Check if we have room to process automation
        if len(self.automations) > 0:

            # Walk through all room
            i = 0
            for room in self.automations:
                i += 1
                print(i)
        i = 0


    # Select room
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
                self.automations.append(datastruct.StructAutomation(sensors, actuators, rule))

        i =0

    # Get rule ba room
    def get_rules_by_room(self, room_rule):
        query = {"name": room_rule}
        return self.__client.sh.automations.find_one(query)

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








