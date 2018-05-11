class RPIInfo():
    def __init__(self, id, ip, port, sensor_ids):
        self.id = id
        self.ip = ip
        self.port = port

        # {'sensor_id': ['Multi Sensor/empty => (1/0)', 'Json => (sensor ok)/HTML => (Sensor error)']}
        self.sensor_ids = sensor_ids
