class StructSensors():
    def __init__(self, dependency, ip, port, devices):
        self.dependency = dependency
        self.ip = ip
        self.port = port
        self.devices = devices


class StructDevices():
    def __init__(self, dependencies, devices, dependency_name):
        self.dependency_name = dependency_name
        self.dependencies = dependencies
        self.devices = devices
