# Z-WAVE network test
# 1) Ping all the RPI to check if available (eg: ping 10.10.5.100)
# 2) Download index page from REST serveur to check if available (eg: wget 10.10.5.100:5000)
# 3) Get all multi-sensors and check if all of them are available (check internal database)


# KNX network test
# 1) Ping physical server which host the REST server and control de KNX network (eg: ping 10.10.5.100)
# 2) Check all the route on the REST server by reading all the shade and radiator (eg:  10.10.5.100:5000//v0/radiator/read/<radiator_id>)
# 3) Get all radiator and shad and check if all of them are available (check internal database)
# 4) Ping the gateway (eg: ping 10.10.5.100)

import utils
import rpi


def main():

    check_zwave_network()


def check_zwave_network():

    rpi_ips = {'rpi1': ['129.194.184.124', 5000], 'rpi2': ['129.194.184.125', 5000], 'rpi3': ['129.194.185.199', 5000]}
    status = {}

    # Check all multi-sensors
    for key, value in rpi_ips.items():

        if utils.send_ping(value[0]):
            status.setdefault(key, []).append("Test1: RPI available")
            if utils.rest_server_status(value[0] + ":" + str(value[1])):
                status.setdefault(key, []).append("Test2: REST server available")
            else:
                status.setdefault(key, []).append("Test2: REST server not available")
        else:
            status.setdefault(key, []).append("Test1: RPI not available")


    # Retrive errors
    for key, value in status.items():
        print(f'Status for {key}: {value}')


def check_knx_network():
    pass


if __name__ == "__main__":
    main()
