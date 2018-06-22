from pymongo import MongoClient
from datetime import datetime
from time import mktime
import matplotlib.pyplot as plt
import time
import const
import sensors
from matplotlib.ticker import NullFormatter  # useful for `logit` scale


def get_smarthepia_datas():

    # YYYY-MM-DD HH:MM:SS
    time_start = int(datetime.strptime("2015-12-23 00:00:00", '%Y-%m-%d %H:%M:%S').timestamp())
    time_stop = int(datetime.strptime("2018-09-05 00:00:00", '%Y-%m-%d %H:%M:%S').timestamp())
    #sensor_id = 18

    # MongoDB database setup
    mdb_client = MongoClient(const.mdb_ip, const.mdb_port)
    #mdb_client.smarthepia.authenticate(const.mdb_username,const.mdb_password)

    plot_measures_by_sensor(mdb_client, time_start, time_stop)


def plot_measures_by_sensor(mdb_client, time_start, time_stop):
    sensor_ids = sensors.get_sensors_list()
    sensor_ids.sort()

    for sensor_id in sensor_ids:

        # Plot measures
        mdb_datas = mdb_client.smarthepia.pi3.find({'$and': [{"sid": sensor_id}, {'ts': {'$gte': time_start}}, {'ts': {'$lte': time_stop}}]})
        plot_measures(list(mdb_datas), sensor_id)


def plot_measures(datas, sensor_id):

    # b, room, h, l, p, t
    measures_type = {'b': ['Battery','%'], 'h': ['Humidity','%'], 'l': ['Liminance','cd/m2'], 'p': ['Presence',''], 't' : ['Temperature','°C']}
    measures = []
    timestamp = []
    subplot = 0
    plt.figure(sensor_id-1)
    plt.suptitle('Measures from Smarthepia multi-sensor (%s) database' % sensor_id, fontsize=16)

    for measure_type, unity in measures_type.items():
        subplot = subplot + 1
        for data in datas:
            status, measure = cleanup_measures_error(data[measure_type], measure_type)

            # Check if error
            if status:
                measures.append(measure)
                current_time = datetime.fromtimestamp(mktime(time.localtime(data['ts'])))
                timestamp.append(current_time)

        plt.subplot(320 + subplot)
        plt.plot(timestamp, measures, label=unity[0])
        plt.xlabel('Time of day')
        plt.ylabel('%s [%s]' % (unity[0], unity[1]))
        plt.legend()
        plt.grid(True)
        measures.clear()
        timestamp.clear()

    plt.gca().yaxis.set_minor_formatter(NullFormatter())
    # Adjust the subplot layout, because the logit one may take more space
    # than usual, due to y-tick labels like "1 - 10^{-3}"
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25, wspace=0.35)
    plt.show()
    plt.gcf().clear()
    plt.clf()
    plt.cla()
    plt.close()


def cleanup_measures_error(value, measure_type):
    if measure_type == 't':
        if value < 45:
            return True, value
        else:
            return False, -1
    elif measure_type == 'p':
        if value:
            return True, 1
        elif not value:
            return True, 0
        else:
            return False, -1
    else:
        return True, value
