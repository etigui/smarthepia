import time
import pymongo
from pymongo.errors import ConnectionFailure
from matplotlib import type1font

import utils


class Sensor(object):

    def __init__(self, sleep_time, ip, port):
        self.sleep_time = sleep_time
        self.__client = None
        self.ip = ip
        self.port = port

    def run(self):
        while True:
            print("Sensor")

            # Init MongoDB client
            status, self.__client = self.db_connect()

            # Check if mongodb has been well init
            if status:

                # Get all dependency devices
                self.get_db_dependency_devices()
            else:
                raise NotImplementedError("Error to implemented (mongodb init error)")
            time.sleep(self.sleep_time)

    # Get all dependency devices
    # Get dependency devices if method (REST/HTTP) is found
    # (REST/HTTP) => REST server for sensor
    def get_db_dependency_devices(self):

        # Get used dependencies by device
        dependencies = self.get_db_devices_dependency_used()
        query = {'$and': [{'depname': {'$in': dependencies}}, {'devices.method': {'$eq': 'REST/HTTP'}}]}
        data_avoid = {'_id': False, '__v': False,'action': False, 'depname': False, 'devices._id': False, 'devices.comment': False, 'devices.name': False }
        devices = self.__client.smarthepia.dependencies.find(query, data_avoid)

        for d in devices:
            for ss in d['devices']:
                if ss['method'] == "REST/HTTP":
                    print(ss)

    # Get all dependency used ba device (Sensor, actuator)
    def get_db_devices_dependency_used(self):
        query = {'$and': [{'type': 'Sensor'}, {'dependency': {'$ne': '-'}}, {'enable': {'$ne': False}}]}
        data_avoid = {'id': False, '_id': False, '__v': False, 'address': False, 'itemStyle': False, 'value': False, 'comment': False, 'group': False, 'rules': False, 'orientation': False, 'action': False, 'name': False, 'type': False, 'parent': False, 'enable': False}
        return utils.append_dependency_to_list(self.__client.smarthepia.devices.find(query, data_avoid))

    # Connect to the database
    def db_connect(self):
        try:
            return True, pymongo.MongoClient(self.ip, self.port)
        except pymongo.errors.ConnectionFailure as e:
            return False, None
