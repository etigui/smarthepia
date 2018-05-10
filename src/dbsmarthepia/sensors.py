import urllib3
import json


def get_sensors_list():
    sensors_id = []
    http = urllib3.PoolManager()
    json_sensors = json.loads(http.request('GET', 'http://129.194.185.199:5000/nodes/get_nodes_list').data)
    for id, name in json_sensors.items():
        if name == 'Multi Sensor':
            sensors_id.append(int(id))
    return sensors_id
