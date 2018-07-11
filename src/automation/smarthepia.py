import multiprocessing
import time

# Local import
import automation
import alarm
import measure
import status_notifier


def smarthepia():

    # Class
    #c_alarm = alarm.Alarm()
    #c_automation = automation.Automation()
    #c_measure = measure.Sensor()
    #c_status = status_notifier.Status()

    # Process
    #p_alarm = multiprocessing.Process(target=c_alarm.run)
    #p_alarm.start()
    #p_automation = multiprocessing.Process(target=c_automation.run)
    #p_automation.start()
    #p_measure = multiprocessing.Process(target=c_measure.run)
    #p_measure.start()

    # Ensure all process have started
    time.sleep(1)
    #p_status = multiprocessing.Process(target=c_status.run)
    #p_status.start()

    # End process (or not)
    #p_alarm.join()
    #p_automation.join()
    #p_measure.join()
    #p_status.join()


if __name__ == "__main__":
    smarthepia()
