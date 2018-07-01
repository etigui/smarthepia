from simple_pid import PID
import time


class StructPid():
    def __init__(self, room_id, pid):
        self.room_id = room_id
        self.pid = pid


class Heater():
    def __init__(self):
        self.__pids = []

    # Get new compute ouput from the PID according to the systems current value
    def get_computed_value(self, room_id, room_ids, indoor_temp, rule_temp: int, kp, ki, kd):

        try:
            # Create new pid if not exist
            # Or if pids list empty
            self.__check_existing_pid(room_id, rule_temp, kp, ki, kd)

            p = self.__get_pid_by_room(room_id)
            if p is not None:

                # Update pid values if user changed
                self.__update_pid(p, rule_temp, kp, ki, kd)

                # Compute new pid value
                computed_value = p.pid(indoor_temp)

                # Sleep to let the pid do his job
                # Otherwise it will give the same value
                time.sleep(1)

                # Clean up unused pid
                self.__check_unused_pid(room_ids)

                # Return new pid computed value
                return True, computed_value, p.pid
            else:
                return False, None, None
        except Exception as e:
            return False, None, None

    # If pid by room not exist create it
    def __check_existing_pid(self, room_id, rule_temp, kp, ki, kd):

        # If no pid by room
        if len(self.__pids) > 0:

            # Get pid by room id
            # If pid not exist create new
            p = self.__get_pid_by_room(room_id)
            if p is None:
                self.__create_pid_by_room(room_id, rule_temp, kp, ki, kd)
        else:
            self.__create_pid_by_room(room_id, rule_temp, kp, ki, kd)

    # Get new pid if new room
    def __create_pid_by_room(self, room_id, rule_temp, kp, ki, kd):
        pid = PID(kp, ki, kd, setpoint=rule_temp)
        pid.output_limits = (0, 255)
        self.__pids.append(StructPid(room_id, pid))

    # Check if unused pid
    def __check_unused_pid(self, room_ids):
        index_to_remove = []
        for index, pid in enumerate(self.__pids):
            if pid.room_id not in room_ids:
                index_to_remove.append(index)

    # Remove unused pid
    def __remove_unused_pid(self, index_to_remove):
        for index in index_to_remove:
            self.__pids.pop(index)


    # Update pid values => kp, ki, kd and temp
    def __update_pid(self, pid, rule_temp, kp, ki, kd):
        pid.setpoint = rule_temp
        pid.tunings = (kp, ki, kd)

    # Get pid by room id store in list
    def __get_pid_by_room(self, room_id):
        for pid in self.__pids:
            if pid.room_id == room_id:
                return pid
        return None


    '''
    def set_valve(self, room):

        # Get consign temp rule
        rule_temp = int(room.rule['temp'])

        # Create new pid by room id if not already exists
        self.create_pid(room.room_id, rule_temp)

        # Get pid by room id
        p = self.get_pid_by_room(room.room_id)
        if p is not None:

            # Update kp, ki, kd and temp
            # That might change in the db
            self.update_pid(p, rule_temp)
            print(f"id: {p.room_id} pid:{id(p.room_id)}")
        else:
            self.automation_log.log_error(f"In function (set_valve), pid by room ({room.room_id}) is not found")

    # Get new pid if new room
    def new_pid_by_room(self, room_id, rule_temp):
        pid = PID(self.automation_rule.kp, self.automation_rule.ki, self.automation_rule.kd, setpoint=rule_temp)
        pid.output_limits = (0, 255)
        self.pids.append(datastruct.StructPid(room_id, pid))

    # Create new pid by room if not exists
    def create_pid(self, room_id, rule_temp):

        # If no pid by room
        if len(self.pids) > 0:

            # Get pid by room id
            # If pid not exist create new
            p = self.get_pid_by_room(room_id)
            if p is None:
                self.new_pid_by_room(room_id, rule_temp)
                print("1")
        else:
            self.new_pid_by_room(room_id, rule_temp)
            print("2")

    # Get pid by room id store in list
    def get_pid_by_room(self, room_id):
        for pid in self.pids:
            if pid.room_id == room_id:
                return pid
        return None

        # Update pid values => kp, ki, kd and temp
    def update_pid(self, pid, rule_temp):
        pid.setpoint = rule_temp
        pid.tunings = (self.automation_rule.kp, self.automation_rule.ki, self.automation_rule.kd)
        
    '''
