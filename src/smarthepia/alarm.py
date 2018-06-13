# email: https://code.tutsplus.com/tutorials/sending-emails-in-python-with-smtp--cms-29975
import time
import datetime
import requests

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


class Alarm(object):

    def __init__(self):
        self.__client = None
        self.ws_status = True
        self.db_status = True

    def run(self):

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
                self.get_db_devices()
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

    # Get all device (sensor, actuator) in the inventory (active, with dependency)
    def get_db_devices(self):
        devices = []
        query = {'$and': [{'$or': [{'type': 'Sensor'}, {'type': 'Actuator'}]}, {'dependency': {'$ne': '-'}}, {'enable': {'$eq': True}}]}
        avoid = {'name': False, 'itemStyle': False,'id': False, '_id': False, '__v': False, 'value': False, 'comment': False, 'group': False, 'rules': False, 'orientation': False, 'action': False, 'type': False, 'enable': False}
        datas = self.__client.sh.devices.find(query, avoid)
        # Get all devices
        for device in datas:
            print(device)
            devices.append(device)
        return devices

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
            response = s.post(const.ws_notify_url_post, data=data)
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
    def check_sensor(self):
        pass

    # Check device with the label type => actuator
    def check_actuator(self):
        pass
