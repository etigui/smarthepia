# email: https://code.tutsplus.com/tutorials/sending-emails-in-python-with-smtp--cms-29975
import time
import datetime
from dateutil.tz import gettz
import requests
import re
import os

# MongoDB driver
import pymongo
from pymongo.errors import ConnectionFailure

# Local import
import utils
import const
import datastruct
import conf
import logger


class Alarm(object):

    def __init__(self):
        self.__client = None
        self.ws_status = True
        self.db_status = True
        self.net_status = False
        self.alarm = []
        self.popup_id = []
        self.admin_email = []
        self.alarm_log = None

    def run(self):

        # Check if log are well init
        if self.log_init():

            # Process alarm
            while True :
                print(f"Alarm: {datetime.datetime.now()}")

                # Init MongoDB client, check connection
                status, self.__client = self.db_connect()

                # Get admin email
                self.get_admin_email()

                # Check web server status
                self.web_server_connect(const.ws_url, const.mc_email_from, self.admin_email, const.mc_password, const.mc_subject)

                # Check if mongodb has been well init
                if status:
                    print(f"DB connection ok: {datetime.datetime.now()}")
                    self.process_network()
                    self.__client.close()
                    self.__client = None
                    self.db_status = True
                else:

                    # Check if the last check was false
                    # if false => we dont send the alarm again until the service goes up again
                    # if true => send mail to admin
                    if self.db_status:

                        # Send mail to the admin, manager if the DB is down
                        self.db_status = False
                        utils.send_database_alert(const.mc_email_from, self.admin_email, const.mc_password, const.mc_subject)

                # Close connection and wait
                time.sleep(const.st_alarm)

    # Init log
    def log_init(self):

        ldp_status , log_dir_path = conf.get_log_dir_path()
        len_status, log_ext_name = conf.get_log_ext_name()
        lfms_status, log_file_max_size = conf.get_log_file_max_size()
        if ldp_status and len_status and lfms_status:
            sp_name = str(os.path.basename(__file__)).replace(".py", "")
            self.alarm_log = logger.Logger(str(log_dir_path), int(log_file_max_size), sp_name, str(log_ext_name))
            self.alarm_log.log_info(f"Subprocess {sp_name} started")
            return True
        else:
            return False

    # Check web server status
    def web_server_connect(self, url, email_from, admin_email, password, subject):

        # HTTP request on web server
        if not utils.get_http(url):

            # Check if the last check was false
            # if false => we dont send the alarm again until the service goes up again
            # if true => send mail to admin
            if self.ws_status:
                self.ws_status = False

                # Send email to all admin
                for email_to in admin_email:
                    utils.send_web_server_alert(email_from, email_to, password, subject)
        else:
            print(f"Web server connection ok: {datetime.datetime.now()}")
            self.ws_status = True

    # Process all the device attached to Smarthepia network
    def process_network(self):

        # To check if we need notify the manager about error
        error = False

        # All dependency and devices
        db_devices = self.get_db_device_and_dependencies()
        for datas in db_devices:

            # Return if error => return false and the devices dependency '_id'
            dependencies_error = self.check_network_dependency(datas.dependencies, datas.dependency_name)

            # Check if at least one dependency is in error
            # If error we dont check device attached to it
            # Cause they wont be available
            if not dependencies_error:
                self.check_network_devices(datas.devices, datas.dependencies)

        # Check if we get error => process and clear
        if len(self.alarm) > 0:
            error = True
            self.process_alarm()
            self.alarm.clear()

        # last status (net_status) = false => no error
        # error = false => no error
        # If last status = false & error = false => We dont need to notify cause nothing change between th last time and now
        if not self.net_status and not error:
            self.net_status = False
        elif not self.net_status and error:  # If last status = false & error = true => notify change
            self.net_status = True
            utils.notify_alarm_change()
        elif self.net_status and not error:  # If last status = true & error = false => notify change cause now no error => all green
            self.net_status = False
            utils.notify_alarm_change()
        else:
            self.net_status = True
            utils.notify_alarm_change()

    # Process all alarm from dependencies and devices
    def process_alarm(self):

        # Dependency device or device error name
        # To add in the graph popup
        device_error = []
        alarm_dependencies = []
        alarm_devices = []

        # Walk through all alarm and sort it by type
        for alarm in self.alarm:
            device_error.append(alarm.name)
            if alarm.type == const.alarm_type_device:
                alarm_devices.append(alarm)
            elif alarm.type == const.alarm_type_dependency:
                alarm_dependencies.append(alarm)
            else:
                print(f"Alarm type ({alarm.type}) not defined")

        # Reset graph
        self.set_all_devices_to_green()

        # Set alarm graph and notif
        self.process_dependencies_alarm(alarm_dependencies)
        self.process_devices_alarm(alarm_devices)

        # Set popup error
        self.set_popup(device_error)

    # Add to each device (id) where error a popup with
    # All the device in error
    def set_popup(self, device_error):

        # Remove duplicate ids
        ids = utils.remove_duplicates(self.popup_id)
        for id in ids:
            query = {'id': id}
            set = {'$push': {"derror": {'$each': device_error}}}
            self.__client.sh.devices.update(query, set)
        self.popup_id.clear()

    # Process alarm and prepare data before to add it to the graph
    def process_dependencies_alarm(self, alarm_dependencies):

        # Set alarm for dependencies
        self.set_alarm(alarm_dependencies)

        # Sort dependency alarm by dependency name
        dependencies = {}
        for alarm in alarm_dependencies:
            dependencies.setdefault(alarm.sub_name, []).append(alarm)

        # Process dependency by dependency name
        for key, value in dependencies.items():
            self.set_dependencies_alarm_graph(key)

    # Set the graph color and popup error
    def set_dependencies_alarm_graph(self, dependency_name):

        query = {'dependency': dependency_name}
        unique_device_id = []
        datas = self.__client.sh.devices.find(query)
        devices = []
        for data in datas:
            devices.append(data)
            unique_device_id.append(data['id'])

        # Get the parent (room) for each device
        # We add it as unique value
        ids_to_change = self.get_hierarchy_id(devices, True)

        # Add multiple element to derror list in db => for each (sensor/actioneur, room, floor, building)
        # Set color for each (sensor/actioneur, room, floor, building)
        for id in ids_to_change:
            query = {'id': id}
            set = {'$set': {"itemStyle.color": const.device_color_error}}
            self.__client.sh.devices.update(query, set)

            # Add device to add popup
            self.popup_id.append(id)

    # Process alarm and prepare data before to add it to the graph
    def process_devices_alarm(self, alarm_devices):

        # Set alarm for devices
        self.set_alarm(alarm_devices)

        # Split sensors and actuators
        alarm_sensors = []
        alarm_actuators = []
        for alarm in alarm_devices:

            # Only add warning and error for the graph
            if alarm.info['type'] == const.warning_alarm or alarm.info['type'] == const.error_alarm:

                # Check if sensor or actuator
                if alarm.sub_type == const.alarm_sub_type_sensor:
                    alarm_sensors.append(alarm)
                else:
                    alarm_actuators.append(alarm)

        # Set graph color, popup error => sensor, actuator
        self.set_sensor_alarm_graph(alarm_sensors)
        self.set_actuator_alarm_graph(alarm_actuators)

    # Set the graph color and popup error for sensor
    def set_sensor_alarm_graph(self, alarm_sensors):

        # Merge sensor by parent(room) to then check if warning or error
        room_sensor_count = {}
        for alarm in alarm_sensors:

            # Only add sensor to list if error
            if alarm.info['type'] == const.error_alarm:
                room_sensor_count[alarm.info['parent']] = room_sensor_count.get(alarm.info['parent'], 0) + 1

        # Iter on merged sensor by parent (room)
        room_error = {}
        for key, value in room_sensor_count.items():
            count = self.get_sensor_room(key)

            # If max sensor are down we must push red to (room, floor, building)
            # Else push orange if not already red
            if count == value:
                room_error[key] = True
            else:
                room_error[key] = False

        # Merge sensor error and warning
        sensor_warning = []
        sensor_error = []
        for alarm in alarm_sensors:

            # If sensor is in warning then it is not in the room_error dico
            if alarm.info['parent'] in room_error:

                # To define if error (max/max)
                # Or if warning (1/max)
                if room_error[alarm.info['parent']]:
                    sensor_error.append(alarm)
                else:
                    sensor_warning.append(alarm)
            else:
                sensor_warning.append(alarm)

        ids_to_change = self.get_hierarchy_id(sensor_error, False)
        for id in ids_to_change:
            query = {'id': id}
            set = {'$set': {"itemStyle.color": const.device_color_error}}
            self.__client.sh.devices.update(query, set)

            # Add device to add popup
            self.popup_id.append(id)

        ids_to_change = self.get_hierarchy_id(sensor_warning, False)
        for id in ids_to_change:

            # Get current color for this id
            query = {'id': id}
            color = self.__client.sh.devices.find_one(query)

            # If the device is not already color error (red)
            # So we change the (device/room/floor/building) to color warning (orange)
            if color['itemStyle']['color'] != const.device_color_error:
                set = {'$set': {"itemStyle.color": const.device_color_warning}}
                self.__client.sh.devices.update(query, set)

                # Add device to add popup
                self.popup_id.append(id)

    # Get number of sensor by room
    # To define if error (max/max)
    # Or if warning (1/max)
    def get_sensor_room(self, parent):
        datas = self.__client.sh.devices.find({"$and": [{"parent": {"$eq": parent}},{"type": {"$eq": "Sensor"}}]})
        return datas.count()

    # Set the graph color and popup error for actuator
    def set_actuator_alarm_graph(self, alarm_actuators):

        # Get hierarchy id, set to graph
        ids_to_change = self.get_hierarchy_id(alarm_actuators, False)
        for id in ids_to_change:
            query = {'id': id}
            set = {'$set': {"itemStyle.color": const.device_color_error}}
            self.__client.sh.devices.update(query, set)

            # Add device to add popup
            self.popup_id.append(id)


    # Set alarm alarm by (dependencies/devices)
    def set_alarm(self, alarms):

        # Walk through alarm by (dependencies/devices)
        for alarm in alarms:

            # Add local date time otherwise mongodb add +02:00
            date_now = datetime.datetime.now(gettz('Europe/Berlin'))

            # Check if device name and ack
            # If length > 1 => we have already an alarm not ack, so we can update
            # Else we create a new alarm entree
            query = {'$and': [{"name": alarm.name}, {"ack": 0}, {"aseverity": alarm.info['severity']},{"atype": alarm.info['type']}]}
            datas = self.__client.sh.alarms.find(query)
            if datas.count() == 0:
                query = {"name": alarm.name, "dtype": alarm.sub_name, "atype": alarm.info['type'],
                         "aseverity": alarm.info['severity'], "amessage": alarm.info['message'], "comment": "", "count": 1,
                         "dstart": date_now, "dlast": date_now,
                         "dend": date_now, "ack": 0, "postpone": date_now,
                         "assign": "anyone", "detail": [date_now]}
                self.__client.sh.alarms.insert(query)
            else:
                # Update device dependency not ack
                # => add new date (new same alarm) fro details
                # => add count + 1
                # => add time last
                value = {'$inc': {'count': 1}, '$set': {"dlast": date_now}, '$push': {"detail": date_now}}
                self.__client.sh.alarms.update(query, value)

    # Get all ids related to devices
    def get_hierarchy_id(self, devices, dependency):
        unique_device_id = []
        for device in devices:
            if dependency:
                unique_device_id.append(device['id'])
            else:
                unique_device_id.append(device.info['id'])

        # If device => info => {dict}
        if not dependency:
            cp_devices = []
            for device in devices:
                cp_devices.append(device.info)
            unique_room_id = utils.add_one_time_value_in_list(cp_devices, "parent")
        else:
            unique_room_id = utils.add_one_time_value_in_list(devices, "parent")

        # Get the parent (room) for each device
        # We add it as unique value
        unique_floor_id = self.get_floor_id(unique_room_id)
        unique_building_id = self.get_building_id(unique_floor_id)
        return unique_room_id + unique_floor_id + unique_building_id + unique_device_id

    # Get all floor ids of room ids
    def get_floor_id(self, unique_room_id):
        floors = []
        query = {'id': {'$in': unique_room_id}}
        datas = self.__client.sh.devices.find(query)
        for data in datas:
            floors.append(data)
        unique_floor_id = utils.add_one_time_value_in_list(floors, "parent")
        return unique_floor_id

    # Get all building ids of floor ids
    def get_building_id(self, unique_floor_id):
        buildings = []
        query = {'id': {'$in': unique_floor_id}}
        datas = self.__client.sh.devices.find(query)
        for data in datas:
            buildings.append(data)
        unique_building_id = utils.add_one_time_value_in_list(buildings, "parent")
        return unique_building_id


    # Check all dependencies
    def check_network_dependency(self, dependencies, dependency_name):

        # To check if dependency error
        error = False

        # Walk through all dependency and
        for dependency in dependencies:

            # Do ping or http get => method
            if dependency['method'] == const.dependency_method_ping:
                if not utils.send_ping(dependency['ip']):
                    error = True
                    self.alarm.append(datastruct.StructAlarm(const.alarm_type_dependency, 0, dependency['name'], dependency_name, {"type": const.error_alarm, "severity": const.severity_high, "message": "No response"}))
            elif dependency['method'] == const.dependency_method_http:

                # Check if port
                # 0 => no port
                # > 0 => get port
                url = "http://"
                if dependency['port'] != 0:
                    url += f"{dependency['ip']}:{dependency['port']}"
                else:
                    url += dependency['ip']

                # Http get with ip
                if not utils.get_http(url):
                    error = True
                    self.alarm.append(datastruct.StructAlarm(const.alarm_type_dependency, 0, dependency['name'], dependency_name, {"type": const.error_alarm, "severity": const.severity_high, "message": "No response"}))
            else:
                print(f"Dependency method ({dependency['method']}) not implemented")

        # Check if dependency error
        if error:
            return True
        else:
            return False

    # Check device available (sensor/actuator)
    def check_network_devices(self, devices, dependencies):

        # Search ip and port for REST dependency
        dependency_ip = ""
        dependency_port = ""
        for dependency in dependencies:
            if dependency['method'] == "REST/HTTP":
                dependency_ip = dependency['ip']
                dependency_port = dependency['port']

        # Process all device
        for device in devices:
            if device['type'] == "Sensor" and device['subtype'] == "Multisensor":

                # Check if sensor are available
                self.check_network_sensor(device, dependency_ip, dependency_port)
            elif device['type'] == "Actuator" and (device['subtype'] == "Valve" or device['subtype'] == "Blind"):

                # Check if actuator with KNX address
                # It could also be actuator but not KNX. In this case GOTO => else
                find = re.findall(r"[\d]{1,2}/[\d]", device['address'])
                if find:

                    # Check if actuator are available
                    self.check_network_actuator(device, dependency_ip, dependency_port)
                else:
                    print(f"Address ({device['address']}) not implemented")
            else:
                print(f"Device type ({device['type']}) or/and subtype ({device['subtype']}) not implemented")

    # Check device with the label type => actuator
    def check_network_actuator(self, device, ip, port):

        # Get id and type to read the value => floor/id
        # id => 1->x
        id = device['address'].split("/")[1]

        # Check what kind of type (radiator/store)
        type = ""
        if device['subtype'] == "Blind":
            type = "store"
        elif device['subtype'] == "Valve":
            type = "radiator"
        else:
            self.alarm.append(datastruct.StructAlarm(const.alarm_type_device, const.alarm_sub_type_actuator, device['name'], device['subtype'], {"id": device['id'], "parent": device['parent'], "type": const.error_alarm,"severity": const.severity_high, "message": "Wrong actuator type"}))
            return

        # Get KNX device value
        route = const.route_knx_device_value_read(ip, port, id, type)
        r = requests.get(route)

        # Error are not displayed as json.... => Node not ready or wrong sensor node type !
        # So we must check the header to convert to json or not
        header = r.headers['content-type']
        if 'text/html' in header:

            # If return != 200 means that server internal error (5xx)
            if r.status_code != 200:
                self.alarm.append(datastruct.StructAlarm(const.alarm_type_device, const.alarm_sub_type_actuator, device['name'], device['subtype'], {"id": device['id'], "parent": device['parent'], "type": const.error_alarm, "severity": const.severity_high, "message": "Actuator id malformed"}))
        else:
            result = r.json()
            if result.get('result'):

                # Check if the sensor id is wrong
                if result['result'] == const.wrong_radiator_id or result['result'] == const.wrong_store_id:
                    self.alarm.append(datastruct.StructAlarm(const.alarm_type_device, const.alarm_sub_type_actuator, device['name'], device['subtype'], {"id": device['id'], "parent": device['parent'], "type": const.error_alarm, "severity": const.severity_high, "message": "Wrong actuator id"}))

    # Check device with the label type => sensor
    def check_network_sensor(self, device, ip, port):

        # Get all measure for a sensor
        r = requests.get(const.route_zwave_device_all_measures(ip, port, device['address']))
        header = r.headers['content-type']

        # Error are not displayed as json.... => Node not ready or wrong sensor node type !
        # So we must check the header to convert to json or not
        if 'text/html' in header:
            r.encoding = "utf-8"
            if r.status_code == 200 and r.text == const.wrong_not_available_device:
                self.alarm.append(datastruct.StructAlarm(const.alarm_type_device, const.alarm_sub_type_sensor, device['name'], device['subtype'], {"id": device['id'], "parent": device['parent'], "type": const.error_alarm, "severity": const.severity_high, "message": "Sensor not exists"}))
            else:
                self.alarm.append(datastruct.StructAlarm(const.alarm_type_device, const.alarm_sub_type_sensor, device['name'], device['subtype'], {"id": device['id'], "parent": device['parent'], "type": const.error_alarm, "severity": const.severity_high, "message": "Wrong sensor id"}))
        else:

            # We sub 2h to now
            # if last updateTime < (now -2h) => means that the sensor is not giving the right value
            result = r.json()
            diff = datetime.datetime.now() + datetime.timedelta(hours=(-2))
            device_update_time = datetime.datetime.fromtimestamp(int(result['updateTime']))
            if device_update_time < diff:
                self.alarm.append(datastruct.StructAlarm(const.alarm_type_device, const.alarm_sub_type_sensor, device['name'], device['subtype'], {"id": device['id'], "parent": device['parent'], "type": const.error_alarm, "severity": const.severity_high, "message": "Device value are not updated"}))
            elif int(result['battery']) < const.battery_min_warning:
                self.alarm.append(datastruct.StructAlarm(const.alarm_type_device, const.alarm_sub_type_sensor, device['name'], device['subtype'], {"id": device['id'], "parent": device['parent'], "type": const.warning_alarm, "severity": const.severity_medium, "message": "Battery less than 10%"}))
            elif int(result['battery']) < const.battery_min_info:
                self.alarm.append(datastruct.StructAlarm(const.alarm_type_device, const.alarm_sub_type_sensor, device['name'], device['subtype'], {"id": device['id'], "parent": device['parent'], "type": const.info_alarm, "severity": const.severity_medium, "message": "Battery less than 20%"}))


    # Empty alarm device array
    # Set green color to the graph
    def set_all_devices_to_green(self):
        datas = self.__client.sh.devices.find({})
        dd = []
        for d in datas:
            dd.append(d)

        for data in dd:
            query = {'id': data['id']}
            set = {'$set': {"itemStyle.color": const.device_color_no_error, "derror": []},}
            self.__client.sh.devices.update(query, set)

    # Get all device (sensor, actuator) in the inventory (active, with dependency)
    def get_db_devices(self):
        devices = []
        query = {'$and': [{'$or': [{'type': 'Sensor'}, {'type': 'Actuator'}]}, {'dependency': {'$ne': '-'}}, {'enable': {'$eq': True}}]}
        avoid = {'itemStyle': False, '_id': False, '__v': False, 'value': False, 'comment': False, 'group': False, 'rules': False, 'orientation': False, 'action': False, 'enable': False} #,'id': False, 'name': False,
        datas = self.__client.sh.devices.find(query, avoid)
        # Get all devices
        for device in datas:
            devices.append(device)
        return devices

    # Get all device dependency and device by dependency
    # Put them together in a struct to check them after
    def get_db_device_and_dependencies(self):
        db_devices = []

        # All device actives
        devices = self.get_db_devices()

        # Get and merge dependency for all active devices
        dependencies = self.append_dependency_to_list(devices)

        # Merge device by dependency
        devices_by_dependency = {}
        for device in devices:
            devices_by_dependency.setdefault(device['dependency'], []).append(device)

        # Get used dependencies devices info by device
        query = {'$and': [{'depname': {'$in': dependencies}}]}
        avoid = {'_id': False, '__v': False, 'devices._id': False, 'action': False, 'devices.comment': False}  # , 'depname': False, , 'devices._id': False ,'devices.name': False
        datas = self.__client.sh.dependencies.find(query, avoid)

        # Build struct with ip, dependency port by device (sensor)
        for data in datas:
            db_devices.append(datastruct.StructDevices(data['devices'], devices_by_dependency[data['depname']], data['depname']))
        return db_devices

    # Append dict item in list if not exist
    def append_dependency_to_list(self, cursor):
        dependencies = []
        dependencies_set = set()
        for item in cursor:
            if item['dependency'] not in dependencies_set:
                dependencies.append(item['dependency'])
                dependencies_set.add(item['dependency'])
        return dependencies

    # Connect to the database
    def db_connect(self):
        try:
            return True, pymongo.MongoClient(const.db_host, const.db_port)
        except pymongo.errors.ConnectionFailure as e:
            return False, None

    # Get admin user email to send critical error
    def get_admin_email(self):

        # If database error
        if self.__client:
            self.admin_email.clear()
            query = {'$and': [{"enable": True}, {"permissions": {'$eq': 2}}]}
            datas = self.__client.sh.users.find(query)

            # Get all devices
            for data in datas:
                self.admin_email.append(data['email'])
        else:

            # Get default email from conf file
            # If db not available
            status, default_email = conf.get_default_email_address()
            if status:

                # Set as default email if db error
                self.admin_email = [default_email]

