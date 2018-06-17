# email: https://code.tutsplus.com/tutorials/sending-emails-in-python-with-smtp--cms-29975
import time
import datetime
from dateutil.tz import gettz
import requests
import re

# MongoDB driver
import pymongo
from pymongo.errors import ConnectionFailure

# Client SMTP
import smtplib
import email.message

# Local import
from html import database
from html import web_server
import utils
import const
import datastruct


class Alarm(object):

    def __init__(self):
        self.__client = None
        self.ws_status = True
        self.db_status = True
        self.net_status = False

    def run(self):

        # Init MongoDB client, check connection
        status, self.__client = self.db_connect()

        self.set_all_devices_to_green()

        d_status = [[{"parent": 7, "name": "MS 53", "dtype": "Sensor", "type": 2, "severity": 1, "message": "Wrong actuator id"}],[{"parent": 7, "name": "MS 2", "dtype": "Sensor", "type": 3, "severity": 3, "message": "Wrong actuator id"}]]
        self.set_device_alarm_and_graph(d_status)
       # self.set_dependency_alarm(dd_status)
        i  = 0

        '''

        # Process alarm
        while True :
            print(f"Alarm: {datetime.datetime.now()}")

            # Check web server status
            self.web_server_connect(const.ws_url, const.mc_email_from, const.mc_email_to, const.mc_password, const.mc_subject)

            # Init MongoDB client, check connection
            status, self.__client = self.db_connect()

            # Check if mongodb has been well init
            if status:
                print(f"DB connection ok: {datetime.datetime.now()}")
                self.process_network()
                self.__client.close()
                self.db_status = True
            else:

                # Check if the last check was false
                # if false => we dont send the alarm again until the service goes up again
                # if true => send mail to admin
                if self.db_status:

                    # Send mail to the admin, manager if the DB is down
                    self.db_status = False
                    self.send_database_status(const.mc_email_from, const.mc_email_to, const.mc_password, const.mc_subject)

            # Close connection and wait
            time.sleep(const.st_alarm)
        '''

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

    # Process all the device attached to Smarthepia network
    def process_network(self):
        d_status = []
        dd_status = []
        error = False

        # All dependency and devices
        db_devices = self.get_db_device_and_dependencies()
        for datas in db_devices:

            # Return if error => return false and the devices dependency '_id'
            dependencies_status, dependency_devices_error = self.check_network_dependency(datas.dependencies, datas.dependency_name)

            # If error add to the list
            if not dependencies_status:
                dd_status.append(dependency_devices_error)

            # If error add to the status list
            if dependencies_status:
                devices_status, devices_error = self.check_network_devices(datas.devices, datas.dependencies)

                # If error add to the status list
                if not devices_status:
                    d_status.append(devices_error)
            else:

                # Set dependencies (building, floor, room, devices) graph to error
                self.set_dependencies_graph_error(datas.dependency_name)

        # Set device graph error and send alarm
        if d_status:
            error = True
            self.set_device_alarm_and_graph(d_status)
            pass

        # Send dependency alarm
        if dd_status:
            self.set_dependency_alarm(dd_status)
            error = True

        # last status (net_status) = false => no error
        # error = false => no error
        # If last status = false & error = false => We dont need to notify cause nothing change between th last time and now
        if not self.net_status and not error:
            self.net_status = False
        elif not self.net_status and error: # If last status = false & error = true => notify change
            self.net_status = True
            #self.notify_alarm_change()
        elif self.net_status and not error: # If last status = true & error = false => notify change cause now no error => all green
            self.net_status = False
            #self.notify_alarm_change()
        else:
            self.net_status = True
            #self.notify_alarm_change()

        i = 0

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

    # Check web server status
    def web_server_connect(self, url, email_from, email_to, password, subject):

        # HTTP request on web server
        if not utils.get_http(url):

            # Check if the last check was false
            # if false => we dont send the alarm again until the service goes up again
            # if true => send mail to admin
            if self.ws_status:
                self.ws_status = False
                self.send_web_server_status(email_from, email_to, password, subject)
        else:
            print(f"Web server connection ok: {datetime.datetime.now()}")
            self.ws_status = True

    # Send mail if the database is down
    def send_database_status(self, email_from, email_to, password, subject):
        message = database.email_html_database(utils.email_splitter(email_to))
        self.send_mail(email_from, email_to, password, message, subject)

    # Send mail if the web server is down
    def send_web_server_status(self, email_from, email_to, password, subject):
        message = web_server.email_html_web_server(utils.email_splitter(email_to))
        self.send_mail(email_from, email_to, password, message, subject)

    # Send mail
    def send_mail(self, email_from, email_to, password, message, subject):

        # Mail content
        msg = email.message.Message()
        msg['Subject'] = subject
        msg['From'] = email_from
        msg['To'] = email_to
        password = password
        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(message)

        # Init client
        client = smtplib.SMTP('smtp.gmail.com: 587')
        client.starttls()

        # Login Credentials for sending the mail
        client.login(msg['From'], password)

        # Send and quit
        client.sendmail(msg['From'], [msg['To']], msg.as_string())
        client.quit()
        print(f"successfully sent html to {msg['To']}")

    # Notify server web when new alarm
    # Then when the web server receive the request
    # it send new alarm in the socket
    def notify_alarm_change(self):
        try:
            s = requests.Session()
            data = {"email": const.ws_notify_email, "password": const.ws_notify_password}
            s.post(const.ws_notify_url_post, data=data)
            response = s.get(const.ws_notify_url_get)

            if response.json() != const.ws_notify_response:
                # TODO it might be a good idea to notify (mail)
                # cause web server is down
                pass
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)

    # Check device with the label type => sensor
    def check_network_sensor(self, device, ip, port):

        r = requests.get(const.route_zwave_device_all_measures(ip, port, device['address']))
        header = r.headers['content-type']

        # Error are not displayed as json.... => Node not ready or wrong sensor node type !
        # So we must check the header to convert to json or not
        if 'text/html' in header:
            r.encoding = "utf-8"
            result = r.text
            if r.status_code == 200 and result == const.wrong_not_available_device:
                return False, {"parent": device['parent'], "name": device['name'], "dtype":device['type'], "type": const.warning_alarm, "severity": const.severity_high, "message": "Sensor not exists"}
            else:
                return False, {"parent": device['parent'], "name": device['name'], "dtype":device['type'],"type": const.warning_alarm, "severity": const.severity_high, "message": "Wrong sensor id"}
        else:
            result = r.json()

            # We sub 2h to now
            # if last updateTime < (now -2h) => means that the sensor is not giving the right value
            diff = datetime.datetime.now() + datetime.timedelta(hours=(-2))
            device_update_time = datetime.datetime.fromtimestamp(int(result['updateTime']))
            if device_update_time < diff:
                return False, {"parent": device['parent'], "name": device['name'], "dtype":device['type'], "type": const.warning_alarm, "severity": const.severity_high, "message": "Device value are not updated"}

            if int(result['battery']) < const.battery_min_warning:
                return False, {"parent": device['parent'], "name": device['name'], "dtype":device['type'], "type": const.warning_alarm, "severity": const.severity_high, "message": "Battery less than 10%"}

            if int(result['battery']) < const.battery_min_info:
                return False, {"parent": device['parent'], "name": device['name'], "dtype":device['type'], "type": const.info_alarm, "severity": const.severity_high, "message": "Battery less than 20%"}
        return True, None

    # Check device with the label type => actuator
    def check_network_actuator(self, device, ip, port):

        # Get id and type to read the value => type/floor/id
        # type => (radiator/store)
        # id => 1->x
        type = device['address'].split("/")[0]
        id = device['address'].split("/")[2]

        # Check what kind of type (radiator/store)
        if type == "1":
            type = "radiator"
        elif type == "2":
            type = "store"
        else:
            return False, {"parent": device['parent'], "name": device['name'], "dtype":device['type'], "type": const.error_alarm, "severity": const.severity_high, "message": "Actuator type"}

        route = const.route_knx_device_value_read(ip, port, id, type)
        r = requests.get(route)

        # Error are not displayed as json.... => Node not ready or wrong sensor node type !
        # So we must check the header to convert to json or not
        header = r.headers['content-type']
        if 'text/html' in header:
            r.encoding = "utf-8"
            result = r.text

            # If return != 200 means that server internal error (5xx)
            if r.status_code != 200:
                return False, {"parent": device['parent'], "name": device['name'], "dtype":device['type'], "type": const.error_alarm, "severity": const.severity_high, "message": "Actuator id malformed"}
        else:
            result = r.json()
            if result.get('result'):

                # Check if the sensor id is wrong
                if result['result'] == const.wrong_radiator_id or result['result'] == const.wrong_store_id:
                    return False, {"parent": device['parent'], "name": device['name'], "dtype":device['type'], "type": const.error_alarm, "severity": const.severity_high, "message": "Wrong actuator id"}
        return True, None

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
        status = []
        for device in devices:
            if device['type'] == "Sensor":

                # If we get sensor info, warning or error => add it to the list to process after
                alarm, infos = self.check_network_sensor(device, dependency_ip, dependency_port)

                # If error add to the status list
                if not alarm:
                    status.append(infos)
            elif device['type'] == "Actuator":

                # Check if actuator with KNX address
                # It could also be actuator but not KNX. In this case GOTO => else
                find = re.findall(r"[\d]{1,2}/[\d]{1,2}/[\d]", device['address'])
                if find:

                    # If we get actuator info, warning or error => add it to the list to process after
                    alarm, infos = self.check_network_actuator(device, dependency_ip, dependency_port)

                    # If error add to the status list
                    if not alarm:
                        status.append(infos)
                else:
                    print(f"Address ({device['address']}) not implemented")
            else:
                print(f"Device type ({device['type']}) not implemented")

        # Check if we have error like warning/info/error
        if status:
            return False, status
        return True, None

    # Check all dependencies
    def check_network_dependency(self, dependencies, dependency_name):
        status = []

        # Walk through all dependency and
        for dependency in dependencies:

            # Do ping or http get => method
            if dependency['method'] == const.dependency_method_ping:
                if not utils.send_ping(dependency['ip']):
                    status.append({"dname": dependency_name, "ddname": dependency['name'], "type": const.error_alarm, "severity": const.severity_high, "message": "No response"})
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
                    status.append({"dname": dependency_name, "ddname": dependency['name'], "type": const.error_alarm, "severity": const.severity_high, "message": "No response"})
            else:
                print(f"Dependency method ({dependency['method']}) not implemented")

        # Check if dependency error
        if status:
            return False, status
        return True, None

    # Find all devices attached to that dependecy and make them as error
    # Must also set building((associate to floor)), floor(associate to room), room(associate to device) as error
    def set_dependencies_graph_error(self, dependency_name):

        self.set_all_devices_to_green()

        query = {'dependency': dependency_name}
        unique_device_id = []
        datas = self.__client.sh.devices.find(query)
        devices = []
        for data in datas:
            devices.append(data)
            unique_device_id.append(data['id'])

        # Get the parent (room) for each device
        # We add it as unique value
        unique_room_id = utils.add_one_time_value_in_list(devices, "parent")

        unique_floor_id = self.get_floor_id(unique_room_id)

        unique_building_id = self.get_building_id(unique_floor_id)

        ids_to_change = unique_room_id + unique_floor_id + unique_building_id + unique_device_id

        for id in ids_to_change:
            query = {'id': id}
            set = {'$set': {"itemStyle.color": const.device_color_error}}
            self.__client.sh.devices.update(query, set)


    def get_floor_id(self, unique_room_id):
        floors = []
        query = {'id': {'$in': unique_room_id}}
        datas = self.__client.sh.devices.find(query)
        for data in datas:
            floors.append(data)
        unique_floor_id = utils.add_one_time_value_in_list(floors, "parent")
        return unique_floor_id


    def get_building_id(self, unique_floor_id):
        buildings = []
        query = {'id': {'$in': unique_floor_id}}
        datas = self.__client.sh.devices.find(query)
        for data in datas:
            buildings.append(data)
        unique_building_id = utils.add_one_time_value_in_list(buildings, "parent")
        return unique_building_id


    def set_all_devices_to_green(self):
        datas = self.__client.sh.devices.find({})
        dd = []
        for d in datas:
            dd.append(d)

        for data in dd:
            query = {'id': data['id']}
            set = {'$set': {"itemStyle.color": const.device_color_no_error}}
            self.__client.sh.devices.update(query, set)

    # Set alarm
    def set_dependency_alarm(self, status):

        for stat in status:
            for device in stat:

                # Add local date time otherwise mongodb add +02:00
                date_now = datetime.datetime.now(gettz('Europe/Berlin'))

                # Check if device name and ack
                # If length > 1 => we have already an alarm not ack, so we can update
                # Else we create a new alarm entree
                query = {'$and': [{"name": device['ddname']}, {"ack": 0}]}
                # TODO change here
                #'$and': [{"name": device['ddname']}, {"ack": 0}, {"aseverity": device['severity']}, {"atype": device['type']}]
                datas = self.__client.sh.alarms.find(query)
                if datas.count() == 0:
                    query = {"name": device['ddname'], "dtype": device['dname'], "atype": device['type'],
                             "aseverity": device['severity'], "amessage": device['message'], "comment": "", "count": 1,
                             "dstart": date_now, "dlast": date_now,
                             "dend": date_now, "ack": 0, "postpone": date_now,
                             "assign": "anyone", "detail": [date_now]}
                    self.__client.sh.alarms.insert(query)
                else:
                    # Update device dependency not ack
                    # => add new date (new same alarm) fro details
                    # => add count + 1
                    # => add time last
                    query = {'$and': [{"name": device['name']}, {"ack": 0}]}
                    value = {'$inc': {'count': 1}, '$set': {"dlast": date_now}, '$push': {"detail": date_now}}
                    self.__client.sh.alarms.update(query, value)

    # Set alarm and color graph
    def set_device_alarm_and_graph(self, status):
        for stat in status:
            for device in stat:

                # Add local date time otherwise mongodb add +02:00
                date_now = datetime.datetime.now(gettz('Europe/Berlin'))

                # Check if device name and ack
                # If length > 1 => we have already an alarm not ack, so we can update
                # Else we create a new alarm entree
                query = {'$and': [{"name": device['name']}, {"ack": 0}, {"aseverity": device['severity']}, {"atype": device['type']}]}
                datas = self.__client.sh.alarms.find(query)
                if datas.count() == 0:
                    query = {"name": device['name'], "dtype": device['dtype'], "atype": device['type'], "aseverity": device['severity'], "amessage": device['message'], "comment": "", "count": 1, "dstart": date_now, "dlast": date_now, "dend": date_now, "ack": 0, "postpone": date_now, "assign": "anyone", "detail": [date_now]}
                    self.__client.sh.alarms.insert(query)
                else:

                    # Update device not ack
                    # => add new date (new same alarm) fro details
                    # => add count + 1
                    # => add time last
                    query = {'$and': [{"name": device['name']}, {"ack": 0}, {"aseverity": device['severity']}, {"atype": device['type']}]}
                    value = {'$inc': {'count': 1}, '$set': {"dlast": date_now}, '$push': {"detail": date_now}}
                    self.__client.sh.alarms.update(query, value)
