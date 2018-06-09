import time
import pymongo

# Local import

class Alarm(object):

    def __init__(self, sleep_time, ip, port):
        self.sleep_time = sleep_time
        self.__client = None
        self.ip = ip
        self.port = port

    def run(self):
        while True :
            print("Alarm")
            time.sleep(self.sleep_time)
