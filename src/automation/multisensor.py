import statistics
import datetime

# Local import
import const
import utils
import weather

# Get sensors by room id
def get_multisensor_by_room(db, room_id):
    sensors = []
    query = {'$and': [{"parent": int(room_id)}, {'subtype': const.db_devices_sub_type_multisensor}]}
    datas = db.sh.devices.find(query)

    # Check if sensor available
    if datas.count() != 0:
        for data in datas:
            sensors.append(data)
        return True, sensors
    else:
        return False, None


# Get measure by multisensor
def get_measure_by_multisensor(db, log, dependency_name, address):
    query = {'$and': [{'depname': dependency_name}, {'devices.method': {'$eq': const.dependency_device_type_rest}}]}
    devices = db.sh.dependencies.find_one(query)

    # Get REST server ip and port
    ip = ""
    port = 0
    for device in devices['devices']:
        if device['method'] == const.dependency_device_type_rest:
            ip = device['ip']
            port = device['port']

    # Get measures by multisensor
    # TODO get_mesures updatted here
    #status, datas = utils.get_mesures(const.route_zwave_device_all_measures(ip, str(port), address))
    status, datas = utils.http_get_request_json(const.route_zwave_device_all_measures(ip, str(port), address))
    if status:
        return True, datas
    log.log_error(f"In function (get_measure_by_multisensor), the multisensor measure could not be given")
    return False, None


# Check all the multisenor for one room
def check_motion_all_multisensors_in_room(db, sensors):

    # Get all multisensor and get dependency name and address
    # to check if motion is recorded
    motion = []
    for sensor in sensors:
        motion_status = check_multisensor_motion(db, sensor['dependency'], sensor['address'])

        # Check if the motion status is not
        # 0 => Nobody in the room
        # 1 => Someone on the room
        # -1 => Multisensor error or date not up to date
        if motion_status == 1:
            motion.append(1)
        elif motion_status == -1:
            motion.append(-1)
        else:
            motion.append(0)

    if 1 in motion:
        return True
    elif 0 in motion:
        return False
    else:
        return True


# Get last 4 motion measure to check if no one is in the room
def check_multisensor_motion(db, dependency, address):

    # Date diff to compare the 4 measures up date time
    diff = datetime.datetime.now() - datetime.timedelta(minutes=25)

    # Get last 4 measure (sorted by _id)
    datas = db.sh.stats.find({'$and': [{"dependency": dependency}, {"address": str(address)}]}).sort([("_id", -1)]).limit(4)

    # Return - if not enough data
    # Or dependency name not fount
    # Or address not fount
    if datas.count() > 4:
        for data in datas:

            # Return -1 if one of the last timestamp if not up to date
            # Last 4 measures cannot be taken if => not up to date
            if data['updatetime'] < diff:
                return -1
            if data['motion']:
                return 1

    else:
        return -1
    return 0


def check_multisensor_time(log, updatetime):

    # Check if the last multisensor measure (temp)
    # are up to date. We check multisensor every 5 min so let say that 6 min is enough
    # To say if the multisensor is up to date
    diff = datetime.datetime.now() - datetime.timedelta(minutes=6)
    measure_update_time = datetime.datetime.fromtimestamp(int(updatetime))

    # Check if the diff is smaller then the current temp
    if diff < measure_update_time:
        return True
    else:
        log.log_error(f"In function (check_multisensor_time), the multisensor is not up to date")
        return False


# Process automation room by room
def check_multisensor(db, log, automation_rule, sensors):

    measures = []
    for sensor in sensors:

        # Get measure by multisensor (http get)
        # Check if response
        measure_status, measure = get_measure_by_multisensor(db, log, sensor['dependency'], sensor['address'])
        if measure_status:

            # Check multisensor timestamp
            # If False => multisensor no uptodate
            time_status = check_multisensor_time(log, measure['updateTime'])
            if time_status:
                measures.append(measure)

    if len(measures) > 0:
        status, temp = check_multisensor_temp(log, automation_rule, measures)
        if status:
            return True, temp, measures
    return False, None, None


# Check if sensors temperature value is enough good
# To rely on it
def check_multisensor_temp(log, automation_rule, measures):

    # If sensor temp value if heigher or lower then max and min threshold
    status, sensors_td = check_threshold_temp(log, automation_rule, measures)

    # Check if we have at least one sensor ok with threshold
    if status:
        if len(sensors_td) == 1:

            # Return first value
            return True, next(iter(sensors_td))
        elif len(sensors_td) >= 2:

            # Check if at least 2 sensor have the same temp
            return True, check_temp_correl(sensors_td)
        else:
            log.log_error(f"In function (check_multisensor_temp), no sensor available to give temp")
            return False, None
    else:
        return False, None


# Check min and max threshold to det if sensor value error
def check_threshold_temp(log, automation_rule, measures):

    # Check if heating period
    hp = weather.check_heat_period(automation_rule)
    sensor_th_check = []
    for measure in measures:

        # If we are in heating period => take other threshold
        if hp:
            min = automation_rule.heater_on_temp_min
            max = automation_rule.heater_on_temp_max
        else:
            min = automation_rule.heater_off_temp_min
            max = automation_rule.heater_off_temp_max

        # Check min and max threshold
        if min < measure['temperature'] < max:
            sensor_th_check.append(measure['temperature'])

    if len(sensor_th_check) > 0:
        return True, sensor_th_check
    log.log_error(f"In function (check_threshold_temp), the min or max threshold passed")
    return False, None


# Correlation between all sensor
def check_temp_correl(sensor_th_check):

    # Get temp median between all sensor temp value
    return statistics.median(sensor_th_check)