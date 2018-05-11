class RPIInfo():
    #def __init__(self, id, ip, port, sensor_ids, status, zwavedb_status):
    def __init__(self, id, ip, port, sensor_ids):
        self.id = id
        self.ip = ip
        self.port = port
        self.sensor_ids = sensor_ids  # {'sensor_id': [status, zwavedb_status]}
        #self.status = status
        #self.zwavedb_status = zwavedb_status