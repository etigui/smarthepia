import urllib3
import pymongo
import json
import rpiinfo
import utils

mdb_host = "192.168.1.111:27017"

# Z-WAVE network test
# 1) Ping all the RPI to check if available (eg: ping 10.10.5.100)
# 2) Download index page from REST serveur to check if available (eg: wget 10.10.5.100:5000)
# 3) Get all multi-sensors and check if all of them are available (check internal database)
#   -> If "Multi Senso" => check (battery, date)
#   -> If "" => check if (Node not ready or wrong sensor node type ! (check if this string in body)) or (battery (check in body if battery))
def check_zwave_network():
    get_db_sensors()

    status = {}

    # id, ip, port, sensor_ids, status, zwavedb_status
    rpi_infos = [(rpiinfo.RPIInfo("rpi1", "129.194.184.124", "5000", [])),
                 (rpiinfo.RPIInfo("rpi2", "129.194.184.125", "5000", [])),
                 (rpiinfo.RPIInfo("rpi3", "129.194.185.199", "5000", []))]

    # Check all multi-sensors
    for info in rpi_infos:

        # Check RPI (ping)
        if utils.send_ping(info.ip):
            status.setdefault(info.id, []).append("Test1: RPI available")

            # Check REST server (ping)
            if utils.rest_server_status(info.ip + ":" + info.port):
                status.setdefault(info.id, []).append("Test2: REST server available")
            else:
                status.setdefault(info.id, []).append("Test2: REST server not available")
        else:
            status.setdefault(info.id, []).append("Test1: RPI not available")

    # Check all multi_sensor availability
    check_sensors(rpi_infos)
    for info in rpi_infos:
        for sensor_id in info.sensor_ids:
            for id, availability in sensor_id.items():
                if availability[0] == '0':
                    if availability[1].find('battery') != -1:
                        status.setdefault(info.id, []).append(f"Test3: sensor {id} available (Mulit Sensor empty)")
                    elif availability[1].find('Node not ready or wrong sensor node type') != -1:
                        status.setdefault(info.id, []).append(f"Test3: sensor {id} not available")
                    else:
                        status.setdefault(info.id, []).append(f"Test3: sensor {id} error (return type unknown)")
                elif availability[0] == '1':
                    status.setdefault(info.id, []).append(f"Test3: sensor {id} available")
                else:
                    status.setdefault(info.id, []).append(f"Test3: sensor {id} error (not 0/1)")


    # Retrive errors
    for key, values in status.items():
        print(f'Status for {key}: {values}')
        print(f'RPI: {key}')
        for value in values:
            print(f'{value}')
        print('')

def get_db_sensors():
    client = pymongo.MongoClient(mdb_host)
    sensors = client.smarthepia.multisensors.find({},{'rpi':True,'_id':False, 'sensor_id': True})
    for sensor in sensors:
        print(sensor)

def check_sensors(rpi_infos):
    for info in rpi_infos:
        get_sensors_list(info)
        check_all_sensors_availability(info)


# Add one sensor to the database
def add_sensors(rpi, sensors_id):
    client = pymongo.MongoClient(mdb_host)
    db = client.smarthepia.multisensors
    for sensor_id in sensors_id:
        db.insert_one({'rpi': rpi, 'sensor_id': sensor_id})


# Get all sensors from each RPI
def get_sensors_list(info):
    http = urllib3.PoolManager()
    json_sensors = json.loads(http.request('GET', 'http://' + info.ip + ':5000/nodes/get_nodes_list').data)
    for id, name in json_sensors.items():
        if name == 'Multi Sensor':
            info.sensor_ids.append({str(id): ["1"]})
        if name == '':
            info.sensor_ids.append({str(id): ["0"]})


# Check all sensors availability
def check_all_sensors_availability(info):
    for ids in info.sensor_ids:
        for id, status in ids.items():
            response = check_sensor_availability(id, info.ip)
            ids[id].append(response)


# Check one sensors availability
def check_sensor_availability(id, ip):
    http = urllib3.PoolManager()
    return http.request('GET', 'http://' + ip + ':5000/sensors/' + str(id) + '/get_all_measures').data.decode("utf-8")
