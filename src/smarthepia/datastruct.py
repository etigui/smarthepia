
# Struct to store sensor
class StructSensors():
    def __init__(self, dependency, ip, port, devices):
        self.dependency = dependency
        self.ip = ip
        self.port = port
        self.devices = devices

# Struct to store devices
class StructDevices():
    def __init__(self, dependencies, devices, dependency_name):
        self.dependency_name = dependency_name
        self.dependencies = dependencies
        self.devices = devices


# Struct to store alarm
class StructAlarm():
    def __init__(self, type, sub_type, name, sub_name, info):
        self.type = type
        self.sub_type = sub_type
        self.name = name
        self.sub_name = sub_name
        self.info = info


# Struct to store automation datas
class StructAutomation():
    def __init__(self, sensors, actuators, rule, orientation, room_id, automation_active):
        self.sensors = sensors
        self.actuators = actuators
        self.rule = rule
        self.orientation = orientation
        self.room_id = room_id
        self.automation_active = automation_active


# Struct to store automation rule
class StructAutomationRule():
    def __init__(self, heater_on_start_day, heater_on_start_month, heater_on_stop_day, heater_on_stop_month, heater_on_temp_min, heater_on_temp_max, heater_off_temp_min, heater_off_temp_max, out_temp_sum_max, kp, ki, kd, out_temp_min, in_temp_min):
        self.heater_on_start_day = heater_on_start_day
        self.heater_on_start_month = heater_on_start_month
        self.heater_on_stop_day = heater_on_stop_day
        self.heater_on_stop_month = heater_on_stop_month
        self.heater_on_temp_min = heater_on_temp_min
        self.heater_on_temp_max = heater_on_temp_max
        self.heater_off_temp_min = heater_off_temp_min
        self.heater_off_temp_max = heater_off_temp_max
        self.out_temp_sum_max = out_temp_sum_max
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.out_temp_min = out_temp_min
        self.in_temp_min = in_temp_min
