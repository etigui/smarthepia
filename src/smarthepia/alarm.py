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


class Alarm(object):

    def __init__(self, sleep_time, ip, port):
        self.sleep_time = sleep_time
        self.__client = None
        self.__smtp_server = None
        self.ip = ip
        self.port = port

    def run(self):
        while True :
            print(f"Alarm: {datetime.datetime.now()}")

            # Init MongoDB client
            status, self.__client = self.db_connect()

            # Check if mongodb has been well init
            if not status:
                print(f"DB connection ok: {datetime.datetime.now()}")
                self.get_db_devices()

            else:

                # Send mail to the admin, manager if the DB is down
                email_from = "smarthepia@gmail.com"
                email_to = "guignard.etienne@gmail.com"
                password = "rvfkEvXg_f0qm5K49_7scAq08BH32AFNCjFaztePJ_Es6YEty8p"
                subject = "Smarthepia network notification"
                message = database.email_html_database()
                self.send_mail(email_from, email_to, password, message, subject)

            # Close connection and wait
            self.__client.close()
            time.sleep(self.sleep_time)

    # Get all device (sensor, actuator) in the inventory (active, with dependency)
    def get_db_devices(self):
        devices = []
        query = {'$and': [{'type': 'Sensor'}, {'dependency': {'$ne': '-'}}, {'enable': {'$eq': True}}]}
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

    # Send mail
    def send_mail(self, email_from, email_to, password, message, subject):

        msg = email.message.Message()
        msg['Subject'] = subject
        msg['From'] = email_from
        msg['To'] = email_to
        password = password
        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(message)

        client = smtplib.SMTP('smtp.gmail.com: 587')
        client.starttls()

        # Login Credentials for sending the mail
        client.login(msg['From'], password)

        client.sendmail(msg['From'], [msg['To']], msg.as_string())
        client.quit()
        print(f"successfully sent html to {msg['To']}")


        '''
        # Create message object instance
        msg = MIMEMultipart()

        # Setup the parameters of the message
        msg['From'] = email_from
        msg['To'] = email_to
        msg['Subject'] = subject

        # Add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # Create server
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()

        # Login Credentials for sending the mail
        server.login(msg['From'], password)

        # Send the message via the server.
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        print("successfully sent html to %s:" % (msg['To']))
        '''