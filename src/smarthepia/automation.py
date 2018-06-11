import time
import pymongo

# Local import
import const


class Automation(object):
    def __init__(self):
        self.__client = None

    def run(self):

        # For first start tempo
        time.sleep(const.st_start)

        # Process automation
        while True :
            print("Automation")
            time.sleep(const.st_automation)
