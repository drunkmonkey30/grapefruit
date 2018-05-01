# deals with capacitive sensors of the game tiles
# this will read sensor state from the microcontroller automatically
# once per time interval, specified by the user
# this class opens an i2c handle that SHOULD be closed when we are done,
#       so don't forget to call close on an instance of this class

try:
    import python_i2c
except:
    print("*** ERROR: python_i2c module not found, continuing without it")

import threading
import math
import time

try:
    import RPi.GPIO
    ON_PI = True
except:
    ON_PI = False


class CapacitiveSensors:
    # initialize class with number of sensors and the time interval for updating
    # capacitive sensor state, defaults to once per second
    def __init__(self, num_sensors=16, time_interval=1.0):
        self.num_sensors = num_sensors

        # sets the number of bytes we will read each time from the microcontroller
        # one bit is used per sensor, so one byte holds state for 8 sensors
        self.sensor_byte_count = int(math.ceil(self.num_sensors / 8.0))

        self.time_interval = time_interval
        if ON_PI:
            self.i2c_handle = python_i2c.i2c_open()
        else:
            self.i2c_handle = -1

        self.update_thread = threading.Thread(target=self.update_sensor_state, name="capsense-updater-0")
        self.update_thread_stop = False

        self.sensor_state = None


    # release i2c handle
    def close(self):
        if ON_PI:
            python_i2c.i2c_close(self.i2c_handle)


    # starts the thread that talks to microcontroller
    def start_update_thread(self):
        self.update_thread.start()


    # this does something completely different
    def stop_update_thread(self):
        self.update_thread_stop = True


    # updates state of the sensors by speaking with the microcontroller over i2c bus
    # NOT TO BE CALLED DIRECTLY
    def update_sensor_state(cap_sense):
        # get initial state of sensors
        if ON_PI:
            cap_sense.sensor_state = python_i2c.i2c_read(cap_sense.i2c_handle, 0x2b, cap_sense.sensor_byte_count)
            for i in range(0, cap_sense.num_sensors):
                print("sensor #" + str(i) + ": " + str(cap_sense.is_sensor_active(i)))
        else:
            print("CapacitiveSensors: read initial state")

        start_time = time.clock()
        while not cap_sense.update_thread_stop:
            delta = time.clock() - start_time
            if delta < cap_sense.time_interval:
                continue

            # delta has passed, read values from microcontroller
            try:
                if ON_PI:
                    cap_sense.sensor_state = python_i2c.i2c_read(cap_sense.i2c_handle, 0x2b, cap_sense.sensor_byte_count)
                    #for i in range(0, cap_sense.num_sensors):
                    #    print("sensor #" + str(i) + ": " + str(cap_sense.is_sensor_active(i)))
                    #print(cap_sense.sensor_state)
                else:
                    print("CapacitiveSensors: update sensor states")
                    pass
            except:
                print("*** ERROR: CapacitiveSensors: failed to read from i2c bus")

            start_time = time.clock()

        # thread has been stopped, exit
        return


    # checks if a sensor is active (something is touching it)
    # returns true or false
    def is_sensor_active(self, sensor_number):
        return self.sensor_state[sensor_number // 8] & (1 << (sensor_number % 8)) != 0


if __name__ == "__main__":
    print("creating cap sense object")
    cap_sense = CapacitiveSensors(16, 1.0)

    print(cap_sense.sensor_byte_count, cap_sense.i2c_handle, cap_sense.time_interval)

    print("testing sensor state check")
    cap_sense.sensor_state = bytearray.fromhex('F1 7b 02')
    print(cap_sense.sensor_state)
    for i in range(0, cap_sense.num_sensors):
        print("sensor #" + str(i) + ": " + str(cap_sense.is_sensor_active(i)))


    cap_sense = CapacitiveSensors(16, 1.0)
    print("\ntesting update thread...")
    cap_sense.start_update_thread()
    try:
        while True:
            pass
    except:
        print("stopping update thread")
        cap_sense.stop_update_thread()
        cap_sense.close()
