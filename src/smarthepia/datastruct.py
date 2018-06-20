
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
