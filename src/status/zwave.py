import urllib3
import pymongo
import json
import datastruct
import utils

'''
# Z-WAVE network test
# 1) Ping all the RPI to check if available (eg: ping 10.10.5.100)
# 2) Download index page from REST serveur to check if available (eg: wget 10.10.5.100:5000)
# 3) Get all multi-sensors and check if all of them are available (check internal database)
#   -> If "Multi Senso" => check (battery, date)
#   -> If "" => check if (Node not ready or wrong sensor node type ! (check if this string in body)) or (battery (check in body if battery))

## Compare DB(info) & REST(info)

{   battery: 100,
    controller: "Pi 1", "Pi 2", "Pi 3"
    humidity: 29,
    location: "A505",
    luminance: 6,
    motion: false,
    sensor: 3,
    temperature: 26.8,
    updateTime: 1526152996}


## Check battery
    if(battery <= 20%)
        print(bettry low)

## Check uptime
    if(updateTime < now - 1J)
        print(uptime error) => the sensor dont send (give) data anymore

'''


def check_zwave_network():

    status = {}
    mdb_host = "192.168.1.111:27017"
    db_sensors = get_db_sensors(mdb_host)

    # Check all multi-sensors
    for db_rpi in db_sensors:

        # Check RPI (ping)
        if utils.send_ping(db_rpi.ip):
            status.setdefault(db_rpi.rpi, []).append([0, db_rpi.rpi,"RPI available"])

            # Check REST server (ping)
            if utils.rest_server_status(db_rpi.ip + ":" + db_rpi.port):
                status.setdefault(db_rpi.rpi, []).append([0, db_rpi.rpi,"REST server available"])

                # Get sensor list from REST server => http://ip:port/nodes/get_nodes_list
                result, rest_sensors = get_sensors_list(db_rpi.ip, db_rpi.port)
                if result:
                    status.setdefault(db_rpi.rpi, []).append([0, db_rpi.rpi, "Route get_nodes_list available"])

                    # db_sensor => (location[0], sensor_id[1], status[2])
                    for db_sensor in db_rpi.sensors:

                        # Mix between RPI name and Sensor id (rpi1.S1 => Raspberry PI1.Sensor1)
                        error_device = f'{db_rpi.rpi}.S{db_sensor[1]}'

                        # If status != 0 => sensor is disabled (no need to check it)
                        if db_sensor[2] == '0':

                            # Check if the sensor id is available in the rest server (compare with db)
                            if db_sensor[1] in rest_sensors:

                                # Get info (REST) from current sensor id => http://ip:port/sensors/sensor_id/get_all_measures
                                result, rest_info = check_sensor_availability(db_sensor[1], db_rpi.ip, db_rpi.port)
                                if result:

                                    # Check if return JSON with sensor info or if the sensor is not available
                                    if rest_info.find('battery') != -1:

                                        # We are sure that we have JSON
                                        rest_info = json.loads(rest_info)

                                        # Check if sensor id from RPI is the same as the sensor id from REST server
                                        # Compare room (A500 => A500) and RPI name (rpi1 => PI 1)
                                        x = rest_info["controller"].replace("Pi ", "rpi")
                                        #status.setdefault(db_rpi.rpi, []).append([0, "Route get_all_measures available"])
                                        print(f'{x} == {db_rpi.rpi}')
                                        print(f'{rest_info["location"]} == {db_sensor[0]}')
                                        if (rest_info['controller'].replace("Pi ", "rpi") == db_rpi.rpi) and (rest_info['location'] == db_sensor[0]):
                                            # status.setdefault(db_rpi.rpi, []).append([0, "Sensor id from REST == sensor id from RPI DB"])
                                            # TODO check timestamp updatetime/battery level
                                            pass
                                        else:
                                            status.setdefault(db_rpi.rpi, []).append([1, error_device, "Sensor id from REST server not match with the RPI DB"])
                                    elif rest_info.find('Node not ready or wrong sensor node type') != -1:
                                        status.setdefault(db_rpi.rpi, []).append([1, error_device, "Sonsor not available"])
                                    else:
                                        status.setdefault(db_rpi.rpi, []).append([1, error_device, "Sonsor error or not available"])
                                else:
                                    status.setdefault(db_rpi.rpi, []).append([1, error_device, "Route get_all_measures not available"])
                            else:
                                status.setdefault(db_rpi.rpi, []).append([1, error_device, "Sensor id not found (REST server)"])
                else:
                    status.setdefault(db_rpi.rpi, []).append([1, db_rpi.rpi, "Route get_nodes_list not available"])

            else:
                status.setdefault(db_rpi.rpi, []).append([1, db_rpi.rpi, "REST server not available"])
        else:
            status.setdefault(db_rpi.rpi, []).append([1, db_rpi.rpi, "RPI not available"])


    # Retrive errors
    for key, values in status.items():
        #print(f'Status for {key}: {values}')
        print(f'RPI: {key}')
        for value in values:
            print(f'{value}')
        print('')


# Get all sensors info from db
def get_db_sensors(mdb_host):

    db_sensors = []
    tmp = {}
    client = pymongo.MongoClient(mdb_host)
    sensors = client.smarthepia.multisensors.find({}, {'_id': False, 'rpi': True, 'ip': True, 'port': True, 'location': True, 'sensor_id': True, 'status': True})

    # Add sensor in dico with key (rpi,ip,port) and list of sensor id
    for sensor in sensors:
        key = f"{sensor['rpi']};{sensor['ip']};{sensor['port']}"
        values = [sensor['location'],sensor['sensor_id'],sensor['status']]
        tmp.setdefault(key, []).append(values)

    # Add all sensors in struct
    for t, v in tmp.items():
        keys = t.split(';')
        db_sensors.append(datastruct.SensorsDB(keys[0], keys[1], keys[2], v))
    return db_sensors


# Get sensors list from REST server
def get_sensors_list(ip, port):
    http = urllib3.PoolManager()
    response = http.request('GET', 'http://' + ip + ':' + port + '/nodes/get_nodes_list')

    # if != 200 => HTTP error
    if response.status != 200:
        return False, {}
    else:
        return True, json.loads(response.data)


# Check one sensors availability
def check_sensor_availability(id, ip, port):
    http = urllib3.PoolManager()
    response = http.request('GET', 'http://' + ip + ':' + port + '/sensors/' + id + '/get_all_measures')

    # if != 200 => HTTP error
    if response.status != 200:
        return False, ""
    else:
        return True, response.data.decode("utf-8")
