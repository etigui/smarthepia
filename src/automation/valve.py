import datetime
from dateutil.tz import gettz

# Local import
import const
import utils

# Save valve setted value
def save_stat_actuator(actuator, db, value):
    # Add local date time otherwise mongodb add +02:00
    #date_now = datetime.datetime.now(gettz('Europe/Berlin'))
    #db.sh.statsacs.insert({'value': value, 'address': actuator['address'], 'dependency': actuator['dependency'], 'parent': actuator['parent'], 'id': actuator['id'], 'updatetime': date_now, 'type': actuator['type'], 'subtype': actuator['subtype'], 'name': actuator['name']})
    db.sh.statsacs.insert({'value': value, 'address': actuator['address'], 'dependency': actuator['dependency'], 'parent': actuator['parent'], 'id': actuator['id'], 'updatetime': datetime.datetime.now(), 'type': actuator['type'], 'subtype': actuator['subtype'], 'name': actuator['name']})


# Close all valve => value = 0
def close_all_valves(db, log, room):
    # Get all actuator by room
    for actuator in room.actuators:

        # Check if blind
        if actuator['subtype'] == const.db_devices_sub_type_valve:

            # Get ip and port for this actuator
            actuator_status, ip, port = get_knx_network_by_device(db, actuator['dependency'])
            if actuator_status:
                close_one_valve(log, ip, port, actuator['address'], actuator, db)


# Close one valve => value = 0
def close_one_valve(log, ip, port, address, actuator, db):

    # Check if the valve is not already close => 0
    # Prevent blind forcing
    valve_read_status, value = get_valve_value(log, ip, port, address)
    if valve_read_status:
        if value != const.valve_min_value:

            # Gen knx route to close valve => 255
            route_status, write_route = const.route_knx_device_value_write(ip, port, address, const.db_devices_sub_type_valve, const.valve_min_value)
            if route_status:
                status, result = utils.http_get_request_json(write_route)
                if not status:
                    # TODO error (maybe alarm) if we cant do it after 20min
                    # Global var list of error blind
                    log.log_error(f"In function (close_one_valve), cannot write pid value ({const.valve_min_value}) to valve")
                else:
                    save_stat_actuator(actuator, db, const.valve_min_value)

# Set the pid computed value for each valve in the room
def set_all_valves(pids, db, log, automation_rule, room, indoor_temp):

    # Get all actuator by room
    for actuator in room.actuators:

        # Check if blind
        if actuator['subtype'] == const.db_devices_sub_type_valve:

            # Get ip and port for this actuator
            actuator_status, ip, port = get_knx_network_by_device(db, actuator['dependency'])
            if actuator_status:

                # Get pid value for the current room to set to valve
                pid_value_status, pid_computed_value = get_pid_by_room(db, log, pids, automation_rule, room, indoor_temp)
                if pid_value_status:
                    set_one_valve(log, ip, port, actuator['address'], pid_computed_value, actuator, db)
                else:
                    log.log_error(f"In function (process_valves), the valve could not be setted")


# Set on valve with pid value
def set_one_valve(log, ip, port, address, pid_computed_value, actuator, db):

    # Check if the valve is not already at pid value
    # Prevent blind forcing
    valve_read_status, value = get_valve_value(log, ip, port, address)
    if valve_read_status:
        if value != pid_computed_value:

            # Gen knx route to close valve => 255
            route_status, write_route = const.route_knx_device_value_write(ip, port, address, const.db_devices_sub_type_valve, pid_computed_value)
            if route_status:
                status, result = utils.http_get_request_json(write_route)
                if not status:
                    # TODO error (maybe alarm) if we cant do it after 20min
                    # Global var list of error blind
                    log.log_error(f"In function (set_one_valve), cannot write pid value ({pid_computed_value}) to valve")
                else:
                    save_stat_actuator(actuator, db, pid_computed_value)


# Get value (read) from valve
def get_valve_value(log, ip, port, address):

    # Check if the valve is not already at max => 255
    # Prevent blind forcing
    read_route = const.route_knx_device_value_read(ip, port, address, const.db_devices_sub_type_valve)
    status, result = utils.http_get_request_json(read_route)
    if not status:
        log.log_error(f"In function (get_valve_value), cannot read value from valve (result={result})")
    else:

        # Check is result label exist
        if "status" in result and "result" in result:
            try:

                # Parse value to int and check if between 0 and 255
                value = int(result['result'])
                if const.valve_min_value <= value <= const.valve_max_value:
                    return True, value
                else:
                    log.log_error(f"In function (get_valve_value), the bind value is not between 0 and 255")
            except ValueError:
                log.log_error(f"In function (get_valve_value), the bind value is not an int")
        else:
            log.log_error(f"In function (get_valve_value), result label are not well formatted")
    return False, None


# Get knx dependency device type REST
# => ip and port
def get_knx_network_by_device(db, dependency_device_name):
    # Get dependency
    query = {'$and': [{'depname': dependency_device_name}, {'devices.method': {'$eq': const.dependency_device_type_rest}}]}
    devices = db.sh.dependencies.find_one(query)
    if devices:

        # Get REST server ip and port
        ip = ""
        port = 0
        for device in devices['devices']:
            if device['method'] == const.dependency_device_type_rest:
                ip = device['ip']
                port = device['port']

        # Check if ip and port not empty
        # => Can be an error if not ip and port
        if ip == "" or port == 0:
            return False, None, None
        return True, ip, port
    return False, None, None


# Get all rooms which contains valves
# Return all the room ids
def get_all_rooms(db):
    room_ids = []
    # Get all rooms
    query = {"type": const.db_devices_type_room}
    datas = db.sh.devices.find(query)
    for data in datas:
        room_id = data['_id']

        # Check if valve in this room
        is_valve = get_valve_by_room(data['id'], db)
        if is_valve:
            # Add room id which contain valve
            room_ids.append(str(room_id))
    return room_ids


# Get actuators by room id
def get_valve_by_room(room_id, db):
    query = {'$and': [{"parent": int(room_id)}, {'subtype': const.db_devices_sub_type_valve}]}
    datas = db.sh.devices.find(query)

    # Check if there is valve
    if datas.count() != 0:
        return True
    else:
        return False


# Get pid value for the current room
def get_pid_by_room(db, log, pids, automation_rule, room, indoor_temp):
    try:

        # Get all rooms which contains valves
        # The class heater will delete (pid) if not in list
        room_ids = get_all_rooms(db)

        # Get rule internal temp
        rule_temp = int(room.rule['temp'])

        # Get computed pid value
        value_status, value, p = pids.get_computed_value(room.room_id, room_ids, indoor_temp, rule_temp, automation_rule.kp, automation_rule.ki, automation_rule.kd)
        if value_status:
            if const.DEBUG: print(f"room id:{room.room_id} pid:{id(p)} value:{value}")
            return True, value
        else:
            log.log_error(f"In function (set_valve), pid by room ({room.room_id}) is not found")
            return False, None
    except Exception as e:
        log.log_error(f"In function (get_pid_by_room), the rule temp could not be casted")
        return False, None
