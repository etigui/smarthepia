# Local import
import const
import utils
import sun
import weather


# Process closing all blind
def close_all_blinds(log, db, actuators):

    # Get all actuator by room
    for actuator in actuators:

        # Check if blind
        if actuator['subtype'] == const.db_devices_sub_type_blind:

            # Get ip and port for this actuator
            actuator_status, ip, port = get_knx_network_by_device(db, actuator['dependency'])
            if actuator_status:
                close_one_blind(log, ip, port, actuator['address'])


# Close one blind
def close_one_blind(log, ip, port, address):

    # Check if the blind is not already at max => 255
    # Prevent blind forcing
    blind_read_status, value = get_blind_value(log, ip, port, address)
    if blind_read_status:
        if value != const.blind_max_value:

            # Gen knx route to close blind => 255
            route_status, write_route = const.route_knx_device_value_write(ip, port, address, const.db_devices_sub_type_blind, const.blind_max_value)
            if route_status:
                status, result = utils.http_get_request_json(write_route)
                if not status:
                    # TODO error (maybe alarm) if we cant do it after 20min
                    # Global var list of error blind
                    log.log_error(f"In function (close_one_blind), cannot write {const.blind_max_value} to blind")


# Get value (read) from blind
def get_blind_value(log, ip, port, address):

    # Check if the blind is not already at max => 255
    # Prevent blind forcing
    read_route = const.route_knx_device_value_read(ip, port, address, const.db_devices_sub_type_blind)
    status, result = utils.http_get_request_json(read_route)
    if not status:
        log.log_error(f"In function (get_blind_value), cannot read value from blind")
    else:

        # Check is result label exist
        if "status" in result and "result" in result:
            try:

                # Parse value to int and check if between 0 and 255
                value = int(result['result'])
                if const.blind_min_value <= value <= const.blind_max_value:
                    return True, value
                else:
                    log.log_error(f"In function (get_blind_value), the bind value is not between 0 and 255")
            except ValueError:
                log.log_error(f"In function (get_blind_value), the bind value is not an int")
        else:
            log.log_error(f"In function (get_blind_value), result label are not well formatted")
    return False, None


# Get knx dependency device type REST
# => ip and port
def get_knx_network_by_device(db, dependency_device_name):
    # Get dependency
    query = {'$and': [{'depname': dependency_device_name}, {'devices.method': {'$eq': const.dependency_device_type_rest}}]}
    devices = db.sh.dependencies.find_one(query)

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


# Rule to close blind when sun and no motion
# In addition we add if hot season and height temp
def rule_sun_and_no_motion(season, automation_rule, log, weather_current, room, sunrise_sunset, is_cloudy):

    # Check if sun anyway
    if sunrise_sunset:

        # If cloud => no sun
        if not is_cloudy:

            # Check if sun in the room
            is_sun, error = sun.is_sun_in_room(room.orientation)
            if error != -1:
                if is_sun:
                    # During spring and summer the temp can reach height temps
                    if season == sun.season_summer or season == sun.season_spring:

                        # Get current external temp
                        temp_status, current_external_temp = weather.get_current_external_temp(log, weather_current)
                        if temp_status:

                            # Check if outside temp is height (base => 25)
                            if current_external_temp >= automation_rule.out_temp_sum_max:
                                return True
                        else:
                            log.log_error(f"In function (rule_sun_and_no_motion), the external temp could not be found")
            else:
                log.log_error(f"In function (process_blinds), the room orientation is not valid")
    return False