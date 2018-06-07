import multiprocessing
import automation
import alarm
import sensor


def main():

    # Set time for each sleep
    factor = 60
    st_alarm = 5 * factor
    st_automation = 60 * factor
    st_sensor = 5# * factor

    # MongoDB connection
    ip = "10.10.0.51"
    port = 27017
    timeout = 2

    # Class
    c_alarm = alarm.Alarm(st_alarm)
    c_automation = automation.Automation(st_automation)
    c_sensor = sensor.Sensor(st_sensor, ip, port, timeout)

    # Process
    p_alarm = multiprocessing.Process(target=c_alarm.run)
    p_alarm.start()
    p_automation = multiprocessing.Process(target=c_automation.run)
    p_automation.start()
    p_sensor = multiprocessing.Process(target=c_sensor.run)
    p_sensor.start()

    # End process (or not)
    p_alarm.join()
    p_automation.join()
    p_sensor.join()


if __name__ == "__main__":
    main()
