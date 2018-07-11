import time
import datetime
import os

# Mongodb driver
import pymongo
from pymongo.errors import ConnectionFailure

# Local import
import utils
import const
import datastruct
import conf
import logger


class Sensor(object):
    def __init__(self):
        self.__client = None
        self.measure_log = None

    def run(self):

        # For first start tempo
        time.sleep(const.st_start)

        # Check if log are well init
        if self.log_init():

            while True:

                if const.DEBUG: print(f"Measure process: {datetime.datetime.now()}")

                # Init MongoDB client
                status, self.__client = self.db_connect()

                # Check if mongodb has been well init
                if status:

                    # Get all dependency devices and device and add to db
                    self.add_db_measures(self.get_db_dependency_devices())

                    # Close db
                    self.__client.close()
                else:
                    self.measure_log.log_error(f"In function (run), could not connect to the db")

                # Wait new iter
                time.sleep(const.st_measure)

    # Init log
    def log_init(self):

        ldp_status , log_dir_path = conf.get_log_dir_path()
        len_status, log_ext_name = conf.get_log_ext_name()
        lfms_status, log_file_max_size = conf.get_log_file_max_size()
        if ldp_status and len_status and lfms_status:
            sp_name = str(os.path.basename(__file__)).replace(".py", "")
            self.measure_log = logger.Logger(str(log_dir_path), int(log_file_max_size), sp_name, str(log_ext_name))
            self.measure_log.log_info(f"Subprocess {sp_name} started")
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

    # Add measures from devices to db
    def add_db_measures(self, db_sensors):
        for dependency in db_sensors:
            for device in dependency.devices:

                # Predefine route for ip, port and device and get measures
                route = const.route_zwave_device_all_measures(dependency.ip, dependency.port, device['address'])
                status, measures = utils.http_get_request_json(route)
                # TODO get_mesures updatted here
                #status, measures = self.get_mesures(route)

                # Check if http error or device address not available or wrong
                if status:

                    # Add to the db to check if the last record alarady exists
                    ref_time = datetime.datetime.fromtimestamp(measures['updateTime'])
                    already_exist = self.__client.sh.stats.find({'$and': [{'address': str(measures['sensor'])}, {'dependency': device['dependency']}, {'reftime': ref_time}]}).count()
                    print(already_exist)
                    if already_exist == 0:
                        self.__client.sh.stats.insert({'address': device['address'], 'dependency': device['dependency'], 'parent': device['parent'], 'battery': measures['battery'], 'temperature': measures['temperature'], 'humidity': measures['humidity'], 'luminance': measures['luminance'], 'motion': measures['motion'], 'updatetime': datetime.datetime.now(), 'reftime': ref_time})
                else:
                    self.measure_log.log_error(f"In function (add_db_measures), the multisensor measure could not be given")

    # Build struct with ip, dependency port by device (multisensor)
    # Get dependency devices if method (REST/HTTP) is found
    # (REST/HTTP) => REST server for sensor
    def get_db_dependency_devices(self):
        db_sensors = []

        # All device actives
        devices = self.get_db_devices()

        # Get and merge dependency for all active devices
        dependencies = self.append_dependency_to_list(devices)

        # Merge device by dependencies
        devices_by_dependency = {}
        for device in devices:
            devices_by_dependency.setdefault(device['dependency'], []).append(device)

        # Get used dependencies devices info by device
        query = {'$and': [{'depname': {'$in': dependencies}}, {'devices.method': {'$eq': 'REST/HTTP'}}]}
        avoid = {'_id': False, '__v': False,'action': False, 'devices._id': False, 'devices.comment': False, 'devices.name': False } # , 'depname': False
        datas = self.__client.sh.dependencies.find(query, avoid)

        # Build struct with ip, dependency port by device (multisensor)
        for data in datas:
            for dep_device in data['devices']:
                if dep_device['method'] == "REST/HTTP":
                    db_sensors.append(datastruct.StructSensors(data['depname'], dep_device['ip'], dep_device['port'], devices_by_dependency[data['depname']]))
        return db_sensors

    # Get all device active and not in error or warning
    def get_db_devices(self):
        devices = []
        query = {'$and': [{'subtype': 'Multisensor'}, {'dependency': {'$ne': '-'}}, {'enable': {'$eq': True}}, {'itemStyle.color': {'$eq': const.device_color_no_error}}]}
        avoid = {'name': False, 'itemStyle': False,'id': False, '_id': False, '__v': False, 'value': False, 'comment': False, 'group': False, 'rules': False, 'orientation': False, 'action': False, 'type': False, 'enable': False}
        datas = self.__client.sh.devices.find(query, avoid)

        # Get all devices
        for device in datas:
            devices.append(device)
        return devices

    # Append dict item in list if not exist
    def append_dependency_to_list(self, cursor):
        dependencies = []
        dependencies_set = set()
        for item in cursor:
            if item['dependency'] not in dependencies_set:
                dependencies.append(item['dependency'])
                dependencies_set.add(item['dependency'])
        return dependencies
