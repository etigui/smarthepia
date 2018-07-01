from simple_pid import PID
import time


def main():
    pid = PID()

    v = 14.34
    #control = pid(v)
    #pid.sample_time = 0.01
    pid.output_limits = (0, 255)
    control = pid(v)
    time.sleep(10)
    print(f"control: {control} and {v}")

    '''
    for i in range(0, 18):
        control = pid(i)
        print(f"control: {control} and {i}")
        time.sleep(1)
    '''

    while True:

        # compute new ouput from the PID according to the systems current value
        control = pid(v)
        print(f"control: {control}")

        v = control


if __name__ == "__main__":
    main()