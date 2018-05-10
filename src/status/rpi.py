import urllib3
import pymongo
import json

def process_sensors(rpi_ips):

    # Check all multi-sensors
    for key, value in rpi_ips.items():
        sensors_id = get_sensors_list(value[0])
        #add_sensors(key, sensors_id)


def add_sensors(rpi, sensors_id):
    client = pymongo.MongoClient('127.0.0.1', 27017)
    db = client.smarthepia.multisensors

    for sensor_id in sensors_id:
        db.insert_one({'rpi': rpi, 'sensor_id': sensor_id})


def get_sensors_list(host):
    sensors_id = []
    http = urllib3.PoolManager()
    json_sensors = json.loads(http.request('GET', 'http://' + host + ':5000/nodes/get_nodes_list').data)
    for id, name in json_sensors.items():
        if name == 'Multi Sensor' or name == '':
            sensors_id.append(int(id))
    return sensors_id
