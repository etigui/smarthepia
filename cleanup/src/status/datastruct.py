class SensorsDB():
    def __init__(self, rpi, ip, port, sensors):
        self.rpi = rpi
        self.ip = ip
        self.port = port
        self.sensors = sensors
        # {'sensor_id': ['Multi Sensor/empty => (1/0)', 'Json => (sensor ok)/HTML => (Sensor error)']}
        #self.sensor_ids = sensor_ids


class RpiDB():
    def __init__(self, rpi, ip, port):
        self.rpi = rpi
        self.ip = ip
        self.port = port


class ZWaveNStatus():
    def __init__(self):
        pass
