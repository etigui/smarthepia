import time
import pymongo

# Local import


class Automation(object):

    def __init__(self, sleep_time, ip, port, st_start):
        self.sleep_time = sleep_time
        self.__client = None
        self.ip = ip
        self.port = port
        self.st_start = st_start

    def run(self):

        # For first start tempo
        time.sleep(self.st_start)
        while True :
            print("Automation")
            time.sleep(self.sleep_time)
