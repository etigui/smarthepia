
# Device status
device_error = '#ff'
device_warning = '#ff'
device_no_error = '#34a046'

# Routes ZWAVE return
wrong_not_available_device = "Node not ready or wrong sensor node type !"


# Routes ZWAVE
def route_node_list(ip, port):
    return f"http://{ip}:{port}/nodes/get_nodes_list"


def route_sensors_list(ip, port):
    return f"http://{ip}:{port}/sensors/get_sensors_list"


def route_device_all_measures(ip, port, address):
    return f"http://{ip}:{port}/sensors/{address}/get_all_measures"


#Routes KNX

