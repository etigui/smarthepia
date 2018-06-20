# Mail client log TODO move it to class var in the future and get email from db
mc_host = "localhost:3000"
mc_url = f"http://{mc_host}"
mc_email_from = "smarthepia@gmail.com"
mc_password = "rvfkEvXg_f0qm5K49_7scAq08BH32AFNCjFaztePJ_Es6YEty8p"
mc_email_to = "guignard.etienne@gmail.com"
mc_subject = "Smarthepia network notification"

# Web server notify login
ws_notify_host = "localhost:3000"
ws_notify_email = "notify@gmail.com"
ws_notify_password = "7scAq08BH3sfh2AFNCjFaztePJ"
ws_notify_url_post = f"http://{ws_notify_host}"
ws_notify_url_get = f"http://{ws_notify_host}/home/alarmnotfy"
ws_notify_response = "alarmNotify"

# Web server check
ws_url = "http://localhost:3000"
ws_help = f"{ws_url}/help"
ws_profile = f"{ws_url}/profile"

# MongoDB database
db_host = "localhost"
db_port = 27017

# Set time for each process sleep
factor = 60
st_alarm = 1 * factor
st_automation = 100 * factor
st_measure = 100 * factor
st_start = 100 * factor

# Device status
device_color_error = '#FF0000'
device_color_warning = '#FFA500'
device_color_no_error = '#34a046'

# Dependency devices method
dependency_method_ping = "Ping"
dependency_method_http = "REST/HTTP"

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
    return f"http://{ip}:{port}/sensors/{address}/get_all_measures"


# Routes KNX
def route_knx_device_value_read(ip, port, id, type):
    return f"http://{ip}:{port}/v0/{type}/read/{id}"

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

# Openweathermap
city_id = "2659667"
api_key = "adeaa68b9d2f5a100919934788d350e0"

return_code_limitation = 429
return_code_success = 200


# Openweathermap routes
def route_current_weather():
    return f"http://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={api_key}"

def route_forecast():
    return f"http://api.openweathermap.org/data/2.5/forecast?id={city_id}&appid={api_key}"



