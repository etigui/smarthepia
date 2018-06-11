# email: https://code.tutsplus.com/tutorials/sending-emails-in-python-with-smtp--cms-29975
import time
import datetime

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


class Alarm(object):

    def __init__(self, sleep_time, ip, port):
        self.sleep_time = sleep_time
        self.__client = None
        self.ip = ip
        self.port = port
        self.ws_status = True
        self.db_status = True

    def run(self):

        # Define client SMTP => TODO move it to class var in the future and get email from db
        email_from = "smarthepia@gmail.com"
        email_to = "guignard.etienne@gmail.com"
        password = "rvfkEvXg_f0qm5K49_7scAq08BH32AFNCjFaztePJ_Es6YEty8p"
        subject = "Smarthepia network notification"
        host = "localhost:3000"
        url = f"http://{host}"

        while True :
            print(f"Alarm: {datetime.datetime.now()}")

            # Check web server status
            # self.web_server_connect(url, host, email_from, email_to, password, subject)

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
                    self.send_database_status(host, email_from, email_to, password, subject)

            # Close connection and wait
            time.sleep(self.sleep_time)

    # Get all device (sensor, actuator) in the inventory (active, with dependency)
    def get_db_devices(self):
        devices = []
        query = {'$and': [{'type': 'Sensor'}, {'type': 'Actuator'}, {'dependency': {'$ne': '-'}}, {'enable': {'$eq': True}}]}
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
            return True, pymongo.MongoClient(self.ip, self.port)
        except pymongo.errors.ConnectionFailure as e:
            return False, None

    # Check web server status
    def web_server_connect(self, url, host, email_from, email_to, password, subject):

        # HTTP request on web server
        if not utils.get_http(url):

            # Check if the last check was false
            # if false => we dont send the alarm again until the service goes up again
            # if true => send mail to admin
            if self.ws_status:
                self.ws_status = False
                self.send_web_server_status(host, email_from, email_to, password, subject)
        else:
            self.ws_status = True

    # Send mail if the database is down
    def send_database_status(self, host, email_from, email_to, password, subject):
        message = database.email_html_database(host, utils.email_splitter(email_to))
        self.send_mail(email_from, email_to, password, message, subject)

    # Send mail if the web server is down
    def send_web_server_status(self, host, email_from, email_to, password, subject):
        message = web_server.email_html_web_server(host, utils.email_splitter(email_to))
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
