import datetime
import time
import random

def main():
    rule_day_time = "08:00"
    rule_night_time = "09:00"

    check = gen_datetime()

    for c in check:
        print(c)

    print(check_night_time(rule_day_time, rule_night_time, datetime.datetime(2010, 8, 6, 7, 1, 0)))


# Check if we are in night time => close all blinds
def check_night_time(rule_day_time, rule_night_time, time_now):

    # Get current date and convert day and night time to time()
    #time_now = datetime.datetime.now().time()
    time_now = time_now.time()
    night_time = datetime.datetime.strptime(f"{rule_night_time}:00", '%H:%M:%S').time()
    day_time = datetime.datetime.strptime(f"{rule_day_time}:00", '%H:%M:%S').time()

    before_midnight = datetime.datetime.strptime(f"23:59:59", '%H:%M:%S').time()
    midnight = datetime.datetime.strptime(f"00:00:00", '%H:%M:%S').time()
    after_midnight = datetime.datetime.strptime(f"00:00:01", '%H:%M:%S').time()

    # Sleep 1 sec if 00:00:00
    if time_now == midnight:
        time_now = after_midnight

    if time_now >= night_time or time_now <= day_time:
        return True
    else:
        return False

# or a function
def gen_datetime():
    check = []
    MINTIME = datetime.datetime(2010, 8, 6, 8, 14, 59)
    MAXTIME = datetime.datetime(2013, 8, 6, 8, 14, 59)
    rule_day_time = "08:00"
    rule_night_time = "00:00"

    mintime_ts = int(time.mktime(MINTIME.timetuple()))
    maxtime_ts = int(time.mktime(MAXTIME.timetuple()))

    for RECORD in range(1000000):
        random_ts = random.randint(mintime_ts, maxtime_ts)
        time_gen = datetime.datetime.fromtimestamp(random_ts)
        check_nt = check_night_time(rule_day_time, rule_night_time, time_gen)
        if not check_nt:
            check.append(f"{time_gen.time()} {check_nt}")
    return check


if __name__ == "__main__":
    main()