import multiprocessing

# Local import
import automation
import alarm
import measure


import requests
import datetime

def main():

    # Class
    #c_alarm = alarm.Alarm()
    c_automation = automation.Automation()
    #c_sensor = measure.Sensor()

    # Process
    #p_alarm = multiprocessing.Process(target=c_alarm.run)
    #p_alarm.start()
    p_automation = multiprocessing.Process(target=c_automation.run)
    p_automation.start()
    #p_sensor = multiprocessing.Process(target=c_sensor.run)
    #p_sensor.start()

    # End process (or not)
    #p_alarm.join()
    p_automation.join()
    #p_sensor.join()


if __name__ == "__main__":
    main()
