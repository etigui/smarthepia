import urllib3
import pymongo
import json


def check_sensors(rpi_infos):
    for info in rpi_infos:
        get_sensors_list(info)
        check_all_sensors_availability(info)


def add_sensors(rpi, sensors_id):
    client = pymongo.MongoClient('127.0.0.1', 27017)
    db = client.smarthepia.multisensors

    for sensor_id in sensors_id:
        db.insert_one({'rpi': rpi, 'sensor_id': sensor_id})


def get_sensors_list(info):
    http = urllib3.PoolManager()
    json_sensors = json.loads(http.request('GET', 'http://' + info.ip + ':5000/nodes/get_nodes_list').data)
    for id, name in json_sensors.items():
        if name == 'Multi Sensor':
            info.sensor_ids.append({str(id): ["1"]})
        if name == '':
            info.sensor_ids.append({str(id): ["0"]})


def check_all_sensors_availability(info):
    for ids in info.sensor_ids:
        for id, status in ids.items():
            response = check_sensor_availability(id, info.ip)
            ids[id].append(response)


def check_sensor_availability(id, ip):
    http = urllib3.PoolManager()
    return http.request('GET', 'http://' + ip + ':5000/sensors/' + str(id) + '/get_all_measures').data.decode("utf-8")
