# Z-WAVE network test
# 1) Ping all the RPI to check if available (eg: ping 10.10.5.100)
# 2) Download index page from REST serveur to check if available (eg: wget 10.10.5.100:5000)
# 3) Get all multi-sensors and check if all of them are available (check internal database)
#   -> If "Multi Senso" => check (battery, date)
#   -> If "" => check if (Node not ready or wrong sensor node type ! (check if this string in body)) or (battery (check in body if battery))


# KNX network test
# 1) Ping physical server which host the REST server and control de KNX network (eg: ping 10.10.5.100)
# 2) Check all the route on the REST server by reading all the shade and radiator (eg:  10.10.5.100:5000//v0/radiator/read/<radiator_id>)
# 3) Get all radiator and shad and check if all of them are available (check internal database)
# 4) Ping the gateway (eg: ping 10.10.5.100)

import utils
import rpi
import rpiinfo


def main():
    check_zwave_network()


def check_zwave_network():

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
    rpi.check_sensors(rpi_infos)
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


def check_knx_network():
    pass


if __name__ == "__main__":
    main()
