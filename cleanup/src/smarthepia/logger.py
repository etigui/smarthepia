import os
import datetime
import re
from pathlib import Path

class Logger():
    def __init__(self, log_path, max_log_file_size, post_ext_name, ext):
        self.log_path = log_path
        self.max_log_file_size = max_log_file_size
        self.ext = ext
        self.post_ext_name = post_ext_name
        self.type_success = "success"
        self.type_info = "info"
        self.type_warning = "warning"
        self.type_error = "error"

        # Write log in file with error as type
    def log_error(self, log_message):
        self.write_log_in_file(f"{self.type_error};{log_message}")

        # Write log in file with warning as type
    def log_warning(self, log_message):
        self.write_log_in_file(f"{self.type_warning};{log_message}")

        # Write log in file with info as type
    def log_info(self, log_message):
        self.write_log_in_file(f"{self.type_info};{log_message}")

    # Write log in file with success as type
    def log_success(self, log_message):
        self.write_log_in_file(f"{self.type_success};{log_message}")

    # Write log in file and add custom log type
    def log_custom_type(self, log_message, log_type="unknown"):
        self.write_log_in_file(f"{log_type};{log_type}")

    def write_log_in_file(self, log_message_and_type):
        try:

            # Get log file name path
            log_file_status, log_file_path = self.get_log_file_path()
            if log_file_status:
                dt = datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")
                with open(log_file_path, "a") as myfile:
                    myfile.write(f"[{dt}];{log_message_and_type}\n")
        except Exception as e:
            pass

    # Check number of log
    def check_max_log_file(self):
        dir_status, log_dir_path = self.get_log_dir_path()
        if dir_status:

            # If we have more then x day log file
            # Remove the last one (oldest)
            files_count = [f for f in os.listdir(log_dir_path) if os.path.isfile(os.path.join(log_dir_path, f)) and self.match_log_file_name(f)]
            if len(files_count) > self.max_log_file_size:

                # Get filename as datetime and remove error file
                files = [self.convert_to_datetime(f) for f in files_count]
                if len(files) > 0:
                    datetime_files = [fd for fd in files if fd != datetime.datetime(1990, 1, 1, 0, 0, 0)]

                    # Remove oldest file
                    if len(datetime_files) > 0:

                        # Convert datetime to log file path
                        convert_status, log_file_path = self.convert_to_log_file(min(datetime_files))
                        if convert_status:

                            # Remove the last one (oldest)
                            return self.remove_file(log_file_path)
        return True


    # Get log file
    def get_log_file_path(self):

        # Check if log dir path exists
        status, log_dir_path = self.get_log_dir_path()
        if status:

            # Concat file and path and check if file exist
            today_file_name = f"{datetime.date.today().strftime('%d_%m_%Y')}.{self.post_ext_name}.{self.ext}"
            file = os.path.join(log_dir_path, today_file_name)

            # If file already exist or not => return full path
            if os.path.isfile(file):
                return True, file
            else:

                # When create new file log check if not max log file
                # If false => dont create log file
                if self.check_max_log_file():
                    return True, file
                else:
                    return False, None
        return False, None

    # Get log directory
    def get_log_dir_path(self):

        # Check if log dir exists
        if os.path.exists(self.log_path):
            return True, self.log_path
        return False, None

    # Convert log file to datime
    def convert_to_datetime(self, log_file_path):
        try:
            file_name = os.path.basename(log_file_path).split('.')[0]
            return datetime.datetime.strptime(str(file_name), '%d_%m_%Y')
        except Exception as e:
            return datetime.datetime(1990, 1, 1, 0, 0, 0)


    # Convert datetime to log file
    def convert_to_log_file(self, log_file_datetime):
        try:

            # Check if log dir path exists
            status, log_dir_path = self.get_log_dir_path()
            if status:
                return True, os.path.join(log_dir_path, f"{log_file_datetime.strftime('%d_%m_%Y')}.{self.post_ext_name}.{self.ext}")
            else:
                return False, None
        except Exception as e:
            return False, None

    # Remove oldest log file
    def remove_file(self, file_path):
        try:
            file = Path(file_path)
            if file.is_file():
                os.remove(file_path)
            return True
        except Exception as e:
            return False

    # Check log file integrity
    def match_log_file_name(self, log_file_name):
        #regex = f"^(\d+_\d+_\d+)[\.]({self.ext})*$"
        regex = f"^(\d+_\d+_\d+)[\.]({self.post_ext_name})*[\.]({self.ext})*$"
        if re.search(rf"{regex}", str(log_file_name)):
            return True
        return False
