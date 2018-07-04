DEBUG = 1

# Process name
process_smarthepia = "smarthepia.py"
process_knxrest = "KNX_REST_Server.py"

# Mail client log TODO move it to class var in the future and get email from db
mc_host = "localhost:3000"
mc_url = f"http://{mc_host}"
mc_email_from = "smarthepia@gmail.com"
mc_password = "rvfkEvXg_f0qm5K49_7scAq08BH32AFNCjFaztePJ_Es6YEty8p"
#mc_email_to_default = "smarthepia@gmail.com"
mc_subject = "Smarthepia network notification"

# Web server notify login
ws_notify_host = "localhost:3000"
ws_notify_email = "notify@gmail.com"
ws_notify_password = "7scAq08BH3sfh2AFNCjFaztePJ"
ws_notify_url_post = f"http://{ws_notify_host}"
ws_alarm_notify_url_get = f"http://{ws_notify_host}/home/alarmnotfy"
ws_alarm_notify_response = "alarmNotify"
ws_status_notify_url_get = f"http://{ws_notify_host}/home/statusnotfy"
ws_status_notify_response = "statusNotify"

# Web server check
ws_url = "http://localhost:3000"
ws_help = f"{ws_url}/help"
ws_profile = f"{ws_url}/profile"

# MongoDB database
db_host = "localhost"
db_port = 27017

# Set time for each process sleep
factor = 60
st_alarm = 5 * factor
st_automation = 1 * factor
st_measure = 5 * factor
st_start = 1 * factor
st_status = 4 * factor

# Device status
device_color_error = '#FF0000'
device_color_warning = '#FFA500'
device_color_no_error = '#34a046'

# Dependency devices method
dependency_method_ping = "Ping"
dependency_method_http = "REST/HTTP"

# Hepia position
lat = 46.20949
lon = 6.135212

# Routes ZWAVE return
wrong_not_available_device = "Node not ready or wrong sensor node type !"

# Route KNX return
wrong_store_id = "Wrong Store ID"
wrong_radiator_id = "Wrong Radiator ID"


# Routes ZWAVE
def route_zwave_node_list(ip, port):
    return f"http://{ip}:{port}/nodes/get_nodes_list"


def route_zwave_device_list(ip, port):
    return f"http://{ip}:{port}/sensors/get_sensors_list"


def route_zwave_device_all_measures(ip, port, address):
    return f"http://{ip}:{str(port)}/sensors/{address}/get_all_measures"


# Routes KNX
def route_knx_device_value_read(ip, port, address, ttype):
    return f"http://{ip}:{str(port)}/v0/{str(ttype).lower()}/read/{address}"


def route_knx_device_value_write(ip, port, address, ttype, value):

    # Check if the value is between 0 and 255
    if blind_min_value < value <= blind_max_value:
        floor = address.split("/")[0]
        id = address.split("/")[1]
        return True, f"http://{ip}:{str(port)}/v0/{str(ttype).lower()}/write/{floor}/{id}/{value}"
    return False, None


# Battery min max value
battery_min_info = 20
battery_min_warning = 10

# Temp after each request (KNX, ZWAVE)
knx_tempo = 0.5
zwave_tempo = 0.5

# Alarm type
error_alarm = 1
warning_alarm = 2
info_alarm = 3

# Severity graduation
severity_low = 1
severity_medium = 2
severity_high = 3

# Alarm type
alarm_type_dependency = 20
alarm_type_device = 10
alarm_sub_type_sensor = 100
alarm_sub_type_actuator = 200

# Database devices collection param
db_devices_type_room = "Room"
db_devices_type_not_location = ["Floor", "Building", "Room"]
db_devices_type_not_location_actuator = db_devices_type_not_location + ["Actuator"]
db_devices_type_not_location_sensor = db_devices_type_not_location + ["Sensor"]

db_devices_sub_type_multisensor = "Multisensor"
db_devices_sub_type_valve = "Valve"
db_devices_sub_type_blind = "Blind"
db_devices_sub_type_actuator = [db_devices_sub_type_valve, db_devices_sub_type_blind]

# Dependency device type REST
dependency_device_type_rest = "REST/HTTP"

# Blind min max value
blind_min_value = 0
blind_max_value = 255
valve_min_value = 0
valve_max_value = 255

# Room angle
room_azimuth_min = 2

# Rule define valve day time
daynight_valve_off = 1
daynight_valve_on = 2

# Rule define blind day time
day_blind_off = 1
day_blind_sam = 2
day_blind_ram = 3
day_blind_full = 4

# Rule define blind night time
night_blind_off = 1
night_blind_on = 2




