import multiprocessing

# Local import
import measures

def main():
    # Class
    c_sensor = measures.Sensor()

    # Process
    p_sensor = multiprocessing.Process(target=c_sensor.run)
    p_sensor.start()

    # End process (or not)
    p_sensor.join()


if __name__ == "__main__":
    main()