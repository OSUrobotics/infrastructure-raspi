#!/usr/bin/env python

from time import time, sleep
import struct
import RPi.GPIO as gpio
from StepperMotor.stepper_motor import StepperMotor
from lower_i2c_controller import lowerController
import smbus2 as smbus


class Testbed():

    def __init__(self):

        # Create dictionary to store object sizes
        # Key is object number, value is height in mm
        self.object_dict =	{
            1: 95,
            2: 95,
            3: 46,
            4: 95
        }

        self.I2Cbus = smbus.SMBus(1)  # shared bus between slave devices
        sleep(1)
        self.lower_slave = lowerController(self.I2Cbus)
        # upper slave device
        self.I2C_SLAVE2_ADDRESS = 14  # 14 is 0x0E
        self.upper_slave = 14  # 14 is 0x0E

        # Variables for moving cone up and down
        self.reset_cone_pul = 20  # pin
        self.reset_cone_dir = 16  # pin
        self.reset_cone_en = 12  # pin  (HIGH to Enable / LOW to Disable)
        self.reset_cone_speed = 0.00001  # default value

        self.lift_time_limit = 6.0  # seconds
        self.lower_time_limit = 2.0  # seconds
        self.goal_angle = 0
        self.angle_error = 1
        # contact plates on the cone - like a button
        self.cone_button = 14  # pin

        self.object_array = [[1, 0, 2, 3, 4], [18, 0, 37, 37, 37]]
        self.previous_object = -1
        self.previous_object_position = 1
        self.need_swap = False

        # Variables for spooling in/out the cable
        self.reset_cable_pul = 19  # pin Green wire
        self.reset_cable_dir = 6  # pin 31 Red wire
        # pin 29 Blue wire (HIGH to Enable / LOW to Disable)
        self.reset_cable_en = 5
        self.reset_cable_speed = 0.00001  # default value

        self.spool_out_time_limit = 4.25  # seconds
        self.spool_in_time_limit = 12  # seconds 
        self.spool_in_time_limit_fast = self.spool_out_time_limit -.5
        self.object_moved = False  # used for edge case if object didn't move during trial

        # hall effect sensor for rotating table
        self.hall_effect = 15  # pin

        # Variables for turntable/encoder wheel
        self.turntable_motor_pwm = 4  # pin 7
        self.turntable_motor_in1 = 21  # pin
        self.turntable_motor_in2 = 27  # pin
        self.turntable_motor_en = 13
        self.lower_arduino_reset_pin = 17

        self.swap_time_limit = 190 # seconds

        # Variables for comunication with arduino for turntable encoder

        # Setting up the pins
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        gpio.setup(self.reset_cone_pul, gpio.OUT)
        gpio.setup(self.reset_cone_dir, gpio.OUT)
        gpio.setup(self.reset_cone_en, gpio.OUT)

        gpio.setup(self.reset_cable_pul, gpio.OUT)
        gpio.setup(self.reset_cable_dir, gpio.OUT)
        gpio.setup(self.reset_cable_en, gpio.OUT)

        # setting up turntable pins
        gpio.setup(self.turntable_motor_pwm, gpio.OUT)
        gpio.setup(self.turntable_motor_in1, gpio.OUT)
        gpio.setup(self.turntable_motor_in2, gpio.OUT)
        gpio.setup(self.turntable_motor_en, gpio.OUT)
        # gpio.setup(self.lower_arduino_reset_pin, gpio.OUT)

        gpio.output(self.turntable_motor_en, gpio.HIGH)
        gpio.output(self.turntable_motor_in1, gpio.LOW)
        # gpio.output(self.lower_arduino_reset_pin, gpio.HIGH)
        gpio.output(self.turntable_motor_in2, gpio.LOW)
        self.turntable_pwm = gpio.PWM(self.turntable_motor_pwm, 1023)
        self.turntable_pwm.start(100)

        # , pull_up_down = gpio.PUD_DOWN)
        gpio.setup(self.hall_effect, gpio.IN)
        gpio.setup(self.cone_button, gpio.IN, pull_up_down=gpio.PUD_DOWN)

        # sets up the stepper motors
        self.reset_cone_motor = StepperMotor(
            self.reset_cone_pul, self.reset_cone_dir, self.reset_cone_en, self.reset_cone_speed)
        self.reset_cable_motor = StepperMotor(
            self.reset_cable_pul, self.reset_cable_dir, self.reset_cable_en, self.reset_cable_speed)
    #----------------------------------------------------------------------------------------------------------------------------#

    def data_transfer(self, data):
        # need to rewrite once working on upper reset
        for num in data:
            if num == 0:
                self.send_transmission(6, self.I2C_SLAVE2_ADDRESS)
                var = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
                self.send_transmission(9, self.I2C_SLAVE2_ADDRESS)
                var = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
                self.send_transmission(7, self.I2C_SLAVE2_ADDRESS)
                var = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
            else:
                self.send_transmission(6, self.I2C_SLAVE2_ADDRESS)
                sleep(.01)
                var = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
                sleep(.01)
                self.send_transmission(num, self.I2C_SLAVE2_ADDRESS)
                sleep(.01)
                var = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
                sleep(.01)
                self.send_transmission(7, self.I2C_SLAVE2_ADDRESS)
                sleep(.01)
                var = self.read_transmission(self.I2C_SLAVE2_ADDRESS)

    def send_swap_data(self, swap_list):
        # need to rewrite once working on upper reset
        b = self.object_array[0]
        c = b.index(swap_list[1])
        swap_list[1] = c
        for num in swap_list:
            self.send_transmission(10, self.I2C_SLAVE2_ADDRESS)
            var = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
            self.send_transmission((num+100), self.I2C_SLAVE2_ADDRESS)
            var = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
            self.send_transmission(11, self.I2C_SLAVE2_ADDRESS)
            var = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
        d = [self.object_array[0][0], self.object_array[1][0]]
        self.object_array[0][0] = self.object_array[0][c]
        self.object_array[1][0] = self.object_array[1][c]
        self.object_array[0][c] = d[0]
        self.object_array[1][c] = d[1]

    #----------------------------------------------------------------------------------------------------------------------------#
    def testbed_reset(self):
        self.cone_reset_up()
        self.cable_reset_spool_in()
        sleep(.5)
        if True:
            print("ho")
            self.cable_reset_spool_out(self.spool_out_time_limit)
            self.cone_reset_down()
            self.turntable_reset_home()
            if self.goal_angle:
                self.turntable_move_angle(self.goal_angle)
            self.need_swap = False
            
        return 1
    #----------------------------------------------------------------------------------------------------------------------------#

    def cone_reset_up(self, time_duration=None):        
        print("cone up")
        if time_duration == None:
            time_duration = self.lift_time_limit
        start_time = time()
        lift_time = 0
        self.lower_slave.limit_switch_mode()
        sleep(0.1)
        self.reset_cone_motor.start_motor(self.reset_cone_motor.CW)
        while True:
            button = self.lower_slave.get_data()
            if lift_time >= self.lift_time_limit or button == 1:
                self.reset_cone_motor.stop_motor()
                if button == 1:
                    print("button was pressed")
                else:
                    print("time ran out")
                break
            lift_time = time() - start_time
    
    #----------------------------------------------------------------------------------------------------------------------------#    

    def cone_reset_down(self, time_duration=None):
        print("cone down")
        if time_duration == None:
            time_duration = self.lower_time_limit
        self.reset_cone_motor.move_for(time_duration, self.reset_cone_motor.CCW)
        
    
    #----------------------------------------------------------------------------------------------------------------------------#

    def cable_reset_spool_in(self):
        print("spool in")
        self.object_moved = False
        self.lower_slave.cone_button_mode()
        sleep(0.1)
        button_val = 0
        self.reset_cone_motor.override_enable()
        start_time = time()
        spool_in_time = 0
        self.reset_cable_motor.start_motor(self.reset_cable_motor.CCW)
        fast = True
        while True:
            button_val = self.lower_slave.get_data()
            if spool_in_time >= self.spool_in_time_limit_fast and fast:
                self.reset_cable_motor.stop_motor()
                self.reset_cable_motor.start_motor(self.reset_cable_motor.CCW, speed=.0003)
                fast = False
            if spool_in_time >= self.spool_in_time_limit or button_val == 1:
                sleep(.01)
                self.reset_cable_motor.stop_motor()
                if spool_in_time < self.spool_out_time_limit/2:
                    # If super short spool in then we actually didn't spool in all the way. Wait for user input and continue
                    status_num = input("Short spool in. Move object and 0 to continue, 1 to stop.")
                    if status_num == 0:
                        self.reset_cable_motor.start_motor(self.reset_cable_motor.CCW)
                        start_time = time()
                        continue
                break
            spool_in_time = time() - start_time
            
    #----------------------------------------------------------------------------------------------------------------------------#

    def cable_reset_spool_out(self, time_duration=None):
        if time_duration == None:
            time_duration = self.spool_out_time_limit
        self.reset_cable_motor.move_for(time_duration, self.reset_cable_motor.CW)
            

     #----------------------------------------------------------------------------------------------------------------------------#

    def turntable_reset_home(self):
        print("resetting home")
        self.lower_slave.hall_effect_mode()
        sleep(0.2)
        hall_effect = self.lower_slave.get_data()
        if hall_effect == 0:
            # already within HE range. To ensure rotation ends at beginning of range, turn for set degrees > range
            print("Already within Home range, moving to guarantee front of range")
            gpio.output(self.turntable_motor_in1, gpio.LOW)
            gpio.output(self.turntable_motor_in2, gpio.HIGH)
            sleep(2.5)  # let turntable move for 2.5 seconds

        gpio.output(self.turntable_motor_in1, gpio.LOW)
        gpio.output(self.turntable_motor_in2, gpio.HIGH)
        while True:
            # turn until find HE (guaranteed to be at beginning of range)
            hall_effect = self.lower_slave.get_data()
            if hall_effect == 0:
                gpio.output(self.turntable_motor_in1, gpio.LOW)
                gpio.output(self.turntable_motor_in2, gpio.LOW)
                print("magnet detected")
                break
            sleep(0.01)
    #----------------------------------------------------------------------------------------------------------------------------#

    def turntable_move_angle(self, goal_angle=20):
        print("moving to angle")
        gpio.output(self.turntable_motor_in1, gpio.LOW)
        gpio.output(self.turntable_motor_in2, gpio.HIGH)
        self.lower_slave.start_counting()
        while True:
            encoder_value = self.lower_slave.get_data()
            print("encoder_value: ", encoder_value)
            if encoder_value >= goal_angle:
                gpio.output(self.turntable_motor_in1, gpio.LOW)
                gpio.output(self.turntable_motor_in2, gpio.LOW)
                print("angle motors stopped at: {}".format(encoder_value))
                break
        sleep(1)  # make sure motors are fully stopped
        print("Angle recorded after motors stopped running: {}".format(
            self.lower_slave.get_data()))
        self.lower_slave.stop_counting()
    
    #----------------------------------------------------------------------------------------------------------------------------#
    # # not being used but can be useful tool in future
    # def lower_arduino_reset(self):
    #     gpio.setup(self.lower_arduino_reset_pin, gpio.OUT)
    #     gpio.output(self.lower_arduino_reset_pin, gpio.LOW)
    #     sleep(.01)
    #     gpio.output(self.lower_arduino_reset_pin, gpio.HIGH)
    #     sleep(3)
    #----------------------------------------------------------------------------------------------------------------------------#

    def object_swap(self, firstObjectID, firstObjectPos, secondObjectID, secondObjectPos):
    #firstObjectHeight = 46, firstObjectPos = 1, secondObjectHeight = 95, secondObjectPos = 2):
        print("got to swap")
        firstObjectHeight = self.object_dict[int(firstObjectID)]
        secondObjectHeight = self.object_dict[int(secondObjectID)]
        print("got to swap2")
        # need to rewrite once working on upper reset
        # self.data_transfer(self.object_array[0])
        # return_value = 0
        # self.send_transmission(2, self.I2C_SLAVE2_ADDRESS)
        # return_value = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
        # self.send_transmission(3, self.I2C_SLAVE2_ADDRESS)
        # self.send_transmission(3, self.I2C_SLAVE2_ADDRESS)

        # while True:
        #     sleep(0.1)
        #     self.send_transmission(3, self.I2C_SLAVE2_ADDRESS)
        #     return_value = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
        #     print(return_value)
        #     if return_value == 3:
        #         break

        # firstObjectHeightBytes = firstObjectHeight.to_bytes(
        #     4, byteorder='little')
        # secondObjectHeightBytes = secondObjectHeight.to_bytes(
        #     4, byteorder='little')

        # temporarily comment out for testing without I2C device
        # self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE2_ADDRESS, 0x00, [
        #     0xaa,
        #     firstObjectHeightBytes[0], firstObjectHeightBytes[1], firstObjectHeightBytes[2], firstObjectHeightBytes[3],
        #     firstObjectPos,
        #     secondObjectHeightBytes[0], secondObjectHeightBytes[1], secondObjectHeightBytes[2], secondObjectHeightBytes[3],
        #     secondObjectPos,
        #     0xff
        # ])

        # TODO: wait for arduino to respond with finished
        # msg = smbus.i2c_msg.read(self.__addr, 2)
        # self.__I2c_bus.i2c_rdwr(msg)
        # raw_list = list(msg)
        # val = (raw_list[0] << 8) + raw_list[1]
        # print(val)
        #first_object_height = 
        print("HERE IN TESTBED ARDUINO")

        print("Sending Lower Reset Code")
        self.cone_reset_up()
        self.cable_reset_spool_in()
        self.cone_reset_up()

        firstObjectHeightBytes = list(bytearray(struct.pack('<L', firstObjectHeight)))
        secondObjectHeightBytes = list(bytearray(struct.pack('<L', secondObjectHeight)))

        print("firstObjectHeightBytes:", firstObjectHeightBytes)
        print("secondObjectHeightBytes:", secondObjectHeightBytes)
    
        self.I2Cbus.write_i2c_block_data(self.upper_slave, 0x00, [
            0xaa,
            firstObjectHeightBytes[0], firstObjectHeightBytes[1], firstObjectHeightBytes[2], firstObjectHeightBytes[3],
            firstObjectPos,
            secondObjectHeightBytes[0], secondObjectHeightBytes[1], secondObjectHeightBytes[2], secondObjectHeightBytes[3],
            secondObjectPos,
            0xff
        ])
        """
        msg = smbus.i2c_msg.read(self.upper_slave, 2) 
        self.I2Cbus.i2c_rdwr(msg)
        raw_list = list(msg)
        val = (raw_list[0] << 8) + raw_list[1]
        """
        start_time = time()
        swap_time = 0
        while True:
            sleep(1)
            try:
                msg = self.I2Cbus.read_byte_data(self.upper_slave, 0x00)
                print("Data:", hex(msg))
            except:
                msg = 0x00
                print("got a weird value, but gonna keep listening")
                continue
            if(msg == 0xF0):
                # Upper arduino sends 0xF0 once complete
                print("Swap Complete")
                break
            elif swap_time > self.swap_time_limit:
                print("Swap/communication failure")
                break
            swap_time = time() - start_time
           

        # self.send_transmission(4, self.I2C_SLAVE2_ADDRESS)
        # return_value = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
        # sleep(4)

        # while True:
        #     sleep(0.1)
        #     self.send_transmission(5, self.I2C_SLAVE2_ADDRESS)
        #     return_value = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
        #     print(return_value)
        #     if return_value == 5:
        #         break

        #self.cable_reset_spool_out()
        #self.cone_reset_down()
        #self.turntable_reset_home()
#----------------------------------------------------------------------------------------------------------------------------#

    def action_caller(self, object_index, object_position, goal_angle):
        print("THERE IN TESTBED ARDUINO")
        if (self.previous_object == -1):
            print("ahh")
            # first run of testbed (assuming desired object is already on testbed)
            self.goal_angle = goal_angle
            # self.testbed_reset()
            self.previous_object = object_index
            self.previous_object_position = object_position
        elif not (object_index == self.previous_object):
            # swap objects

            # self.send_swap_data([0, object_index])
            # self.data_transfer(self.object_array[1])
            self.need_swap=True
            print("Swapping objects:", object_index)
            #self.object_swap(object_index)
            self.object_swap(self.previous_object, int(self.previous_object_position), object_index, int(object_position))            

            self.goal_angle = goal_angle
            self.previous_object = object_index
            self.previous_object_position = object_position

            # temporarily comment out for testing without I2C device
            # if not (goal_angle == 0):
            #     self.turntable_move_angle(goal_angle)
        else:
            # same object
            print("heck")
            self.goal_angle = goal_angle
            # self.testbed_reset()
        # print("\nfinished first call\n")
        return
#----------------------------------------------------------------------------------------------------------------------------#


if __name__ == '__main__':

    test_num = input("""
0) Run bottom reset
1) spool_out
2) spool_in
3) cone_up
4) cone_down
5) turntable_home
6) turntable_angle
7) Object Swap
What do you want to test? (enter the number)
""")

    reset_testbed = Testbed()
    if test_num == 0:
        reset_testbed.goal_angle = 360
        for i in range(1):
            sleep(3)  # give me time to move object
            print("trial {}".format(i+1))
            reset_testbed.testbed_reset()

    elif test_num == 1:
        reset_testbed.object_moved = True
        reset_testbed.cable_reset_spool_out(4.5)
        

    elif test_num == 2:
        reset_testbed.cable_reset_spool_in()

    elif test_num == 3:
        reset_testbed.cone_reset_up()

    elif test_num == 4:
        reset_testbed.cone_reset_down()

    elif test_num == 5:
        reset_testbed.turntable_reset_home()

    elif test_num == 6:
        angle = input("\nwhat angle do you want to rotate by?  (Degrees)\n")
        
        reset_testbed.turntable_move_angle(angle)

    elif test_num == 7:
        # add function here
        reset_testbed.object_swap()

    else:
        print("\nNot implemented\n")
#----------------------------------------------------------------------------------------------------------------------------#
