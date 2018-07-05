import datetime
import utils
import const
import os
import time
from platform import system as system_name
import psutil

# MongoDB driver
import pymongo
from pymongo.errors import ConnectionFailure

# Local import
import conf
import logger


class Status(object):
    def __init__(self):
        self.__client = None
        self.status_log = None

    def run(self):

        # Check if log are well init
        if self.log_init():

            while True:

                if const.DEBUG: print(f"Status process: {datetime.datetime.now()}")

                # Init MongoDB client
                status, self.__client = self.db_connect()
                if status:

                    # Update every 5 min the status of KNX REST and automation
                    notify_status = self.check_sh_status()
                    if not notify_status:
                        self.status_log.log_error(f"In function (run), the alarm notify could not be sent")

                    # Close db
                    self.__client.close()
                else:
                    self.status_log.log_error(f"In function (run), could not connect to the db")

                # Wait nest iter
                time.sleep(const.st_status)

    # Init log
    def log_init(self):

        ldp_status , log_dir_path = conf.get_log_dir_path()
        len_status, log_ext_name = conf.get_log_ext_name()
        lfms_status, log_file_max_size = conf.get_log_file_max_size()
        if ldp_status and len_status and lfms_status:
            sp_name = str(os.path.basename(__file__)).replace(".py", "")
            self.status_log = logger.Logger(str(log_dir_path), int(log_file_max_size), sp_name, str(log_ext_name))
            self.status_log.log_info(f"Subprocess {sp_name} started")
            return True
        else:
            return False

    # Connect to the database
    def db_connect(self):
        try:
            client = pymongo.MongoClient(const.db_host, const.db_port, serverSelectionTimeoutMS=1)
            client.server_info()
            if client is not None:
                return True, client
            else:
                return False, None
        except pymongo.errors.ConnectionFailure as e:
            return False, None

    # Check every 5 min the status of KNX REST and automation
    def check_sh_status(self):

        # Try to prevent big error
        try:

            # Get current datetime
            new_date = datetime.datetime.now().strftime("%H:%M:%S %m-%d-%Y")

            # Check process and notify client of new status
            self.check_automation( new_date)
            self.check_knxrest(new_date)
            return utils.notify_alarm_change(const.ws_status_notify_url_get, const.ws_status_notify_response)
        except Exception as e:
            return False

    # Check and Update/insert automation status
    def check_automation(self, new_date):
        if system_name().lower() != 'windows':

            # We must have 4 smarthepia process
            count = self.check_process(const.process_smarthepia)
            if count == 4:
                self.__client.sh.status.update({"name": "automation"}, {'$set': {"color": 1, "status": "Running 4/4", "name": "automation", "updatetime": new_date}},upsert=True)
            elif 0 < count <= 4:
                self.__client.sh.status.update({"name": "automation"}, {'$set': {"color": 2, "status": f"Running {count}/4", "name": "automation", "updatetime": new_date}},upsert=True)
            else:
                self.__client.sh.status.update({"name": "automation"}, {'$set': {"color": 3, "status": f"Not running", "name": "automation", "updatetime": new_date}},upsert=True)
        else:
            self.__client.sh.status.update({"name": "automation"}, {'$set': {"color": 1, "status": "Running 4/4 win", "name": "automation", "updatetime": new_date}},upsert=True)

    # Check and Update/insert KNX REST status
    def check_knxrest(self, new_date):
        if system_name().lower() != 'windows':

            # We must have at least one KNX REST process started
            count = self.check_process(const.process_knxrest)
            if count == 1:
                self.__client.sh.status.update({"name": "knx"}, {'$set': {"color": 1, "status": "Running", "name": "knx", "updatetime": new_date}}, upsert=True)
            else:
                self.__client.sh.status.update({"name": "knx"}, {'$set': {"color": 3, "status": "Not running", "name": "knx", "updatetime": new_date}}, upsert=True)
        else:
            self.__client.sh.status.update({"name": "knx"},{'$set': {"color": 1, "status": "Running win", "name": "knx", "updatetime": new_date}},upsert=True)

    # Count number of process running by process name
    def check_process(self, process_name):

        # Check all process available
        count = 0
        for pid in psutil.pids():
            p = psutil.Process(pid)

            # Check if the process is alive
            if p.status() not in (psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD, psutil.STATUS_STOPPED):

                # Check python3 which exec the script
                if p.name() == "python3":

                    # Check process name to find
                    if process_name in p.cmdline():
                        count += 1
        return count
