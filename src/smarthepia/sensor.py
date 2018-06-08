import time
import urllib3
import json
import pymongo
import datetime
from pymongo.errors import ConnectionFailure

# Local import
import utils
import const
import datastruct


class Sensor(object):

    def __init__(self, sleep_time, ip, port):
        self.sleep_time = sleep_time
        self.__client = None
        self.ip = ip
        self.port = port

    def run(self):
        while True:

            print(f"Sensor: {datetime.datetime.now()}")

            # Init MongoDB client
            status, self.__client = self.db_connect()

            # Check if mongodb has been well init
            if status:
                print("DB connection ok")

                # Get all dependency devices and device and add to db
                self.add_db_measures(self.get_db_dependency_devices())

            else:
                raise NotImplementedError("Error to implemented (mongodb init error)")
            time.sleep(self.sleep_time)

    # Add measures from devices to db
    def add_db_measures(self, db_sensors):

        for dependency in db_sensors:
            for device in dependency.devices:

                # Predefine route for ip, port and device and get measures
                route = const.route_device_all_measures(dependency.ip, dependency.port, device['address'])
                status, measures = self.get_mesures(route)

                # Check if http error or device address not available or wrong
                if status:
                    self.__client.smarthepia.statistics.insert({'address': device['address'], 'dependency': device['dependency'], 'parent': device['parent'], 'battery': measures['battery'], 'temperature': measures['temperature'], 'humidity': measures['humidity'], 'luminance': measures['luminance'], 'motion': measures['motion'], 'updatetime': datetime.datetime.now()})

    # Get device measures
    def get_mesures(self, route):
        http = urllib3.PoolManager()
        response = http.request('GET', route)

        # if != 200 => HTTP error
        if response.status == 200:
            data = response.data.decode("utf-8")
            if data != const.wrong_not_available_device:
                return True, json.loads(data)
            print(f"Sensor error wrong: {route}")
            return False, {}
        else:
            print("Sensor error 200")
            return False, {}


    # Build struct with ip, dependency port by device (sensor)
    # Get dependency devices if method (REST/HTTP) is found
    # (REST/HTTP) => REST server for sensor
    def get_db_dependency_devices(self):
        db_sensors = []

        # All device actives
        devices = self.get_db_devices()

        # Get and merge dependency for all active devices
        dependencies = utils.append_dependency_to_list(devices)

        # Merge device by dependencies
        dependencies_devices = {}
        for device in devices:
            dependencies_devices.setdefault(device['dependency'], []).append(device)

        # Get used dependencies devices info by device
        query = {'$and': [{'depname': {'$in': dependencies}}, {'devices.method': {'$eq': 'REST/HTTP'}}]}
        avoid = {'_id': False, '__v': False,'action': False, 'devices._id': False, 'devices.comment': False, 'devices.name': False } # , 'depname': False
        datas = self.__client.smarthepia.dependencies.find(query, avoid)

        # Build struct with ip, dependency port by device (sensor)
        for data in datas:
            for dep_device in data['devices']:
                if dep_device['method'] == "REST/HTTP":
                    db_sensors.append(datastruct.StructSensors(data['depname'], dep_device['ip'], dep_device['port'], dependencies_devices[data['depname']]))
        return db_sensors

    # Get all device active and not in error or warning
    def get_db_devices(self):
        devices = []
        query = {'$and': [{'type': 'Sensor'}, {'dependency': {'$ne': '-'}}, {'enable': {'$eq': True}}, {'itemStyle.color': {'$eq': const.device_no_error}}]}
        avoid = {'name': False, 'itemStyle': False,'id': False, '_id': False, '__v': False, 'value': False, 'comment': False, 'group': False, 'rules': False, 'orientation': False, 'action': False, 'type': False, 'enable': False}
        datas = self.__client.smarthepia.devices.find(query, avoid)

        # Get all devices
        for device in datas:
            devices.append(device)
        return devices

    # Connect to the database
    def db_connect(self):
        try:
            return True, pymongo.MongoClient(self.ip, self.port)
        except pymongo.errors.ConnectionFailure as e:
            return False, None
