import time
import pymongo


class Alarm(object):

    def __init__(self, sleep_time):
        self.sleep_time = sleep_time

    def run(self):
        while True :
            print("Alarm")
            time.sleep(self.sleep_time)
