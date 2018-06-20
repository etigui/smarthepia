import time
from pysolar.solar import *
import datetime

# MongoDB driver
import pymongo
from pymongo.errors import ConnectionFailure

# Local import
import const
import utils


class Automation(object):
    def __init__(self):
        self.__client = None

    def run(self):

        # For first start tempo
        #time.sleep(const.st_start)

        # Process automation
        while True :
            print("Automation")
            # Init MongoDB client
            status, self.__client = self.db_connect()



            self.__client.close()
            time.sleep(const.st_automation)


    # Connect to the database
    def db_connect(self):
        try:
            return True, pymongo.MongoClient(const.db_host, const.db_port)
        except pymongo.errors.ConnectionFailure as e:
            return False, None

    # Get last forecast from api or db if fail
    def get_api_forecast(self):

        # If error we get last data from db
        status, api_datas = utils.get_forecast()
        if status:
            self.__client.sh.currents.insert(api_datas)
            return api_datas
        else:
            return self.get_db_forecast()

    # Get last current weather from api or db if fail
    def get_api_current_weather(self):

        # Get last measures from db
        db_datas = self.get_db_current_weather()

        # Get last measures from api
        status, api_datas = utils.get_current_weather()

        # If get measures from api
        if status:

            # If the api have a new measures then we add it to the db and return it
            # Else give last measure from db
            if datetime.datetime.fromtimestamp(int(db_datas['dt'])) < datetime.datetime.fromtimestamp(int(api_datas['dt'])):
                self.__client.sh.currents.insert(api_datas)
                return api_datas
            else:
                return db_datas
        else:
            return db_datas

    # Get last current weather measure from db
    def get_db_current_weather(self):
        return self.__client.sh.currents.find_one({'$query': {}, '$orderby': {'$natural': -1}})

    # Get last forecast measure from db
    def get_db_forecast(self):
        return self.__client.sh.forecasts.find_one({'$query': {}, '$orderby': {'$natural': -1}})








