import json

# Conf file info
file_name = "conf.json"
label_email_default = "defaultErrorEmail"
label_log_dir_path = "logDirPath"
label_log_ext_name = "logExtName"
label_log_file_max_size = "logFileMaxSize"


# Get conf data from json file
def get_conf_by_label(label):
    try:
        with open(file_name) as f:
            data = json.load(f)
            return True, data[label]
    except Exception as e:
        return False, None


# Get default email to send error
# If db is not available
def get_default_email_address():
    return get_conf_by_label(label_email_default)


# Get log directory to store log file
def get_log_dir_path():
    return get_conf_by_label(label_log_dir_path)


# Get ext for log file
def get_log_ext_name():
    return get_conf_by_label(label_log_ext_name)

# Get max log file to keep
def get_log_file_max_size():
    return get_conf_by_label(label_log_file_max_size)