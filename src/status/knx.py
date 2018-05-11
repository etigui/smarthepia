
# KNX network test
# 1) Ping physical server which host the REST server and control de KNX network (eg: ping 10.10.5.100)
# 2) Check all the route on the REST server by reading all the shade and radiator (eg:  10.10.5.100:5000//v0/radiator/read/<radiator_id>)
# 3) Get all radiator and shad and check if all of them are available (check internal database)
# 4) Ping the gateway (eg: ping 10.10.5.100)
def check_knx_network():
    pass