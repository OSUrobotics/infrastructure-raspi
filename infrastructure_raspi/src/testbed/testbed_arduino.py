#!/usr/bin/env python

from time import time, sleep
import RPi.GPIO as gpio
from stepper_motor import StepperMotor
from lower_i2c_controller import lowerController
import smbus2 as smbus

class Testbed():

    def __init__(self):
        
        self.I2Cbus = smbus.SMBus(1) # shared bus between slave devices
        self.lower_slave = lowerController(self.I2Cbus)
        # upper slave device
        self.I2C_SLAVE2_ADDRESS = 14

        
        # Variables for moving cone up and down
        self.reset_cone_pul = 16 # pin
        self.reset_cone_dir = 20  # pin
        self.reset_cone_en = 12  # pin  (HIGH to Enable / LOW to Disable)
        self.reset_cone_speed = 0.00001 # default value

        
        
        self.lift_time_limit = 6.0  # seconds
        self.lower_time_limit = 2.0  # seconds
        self.goal_angle = 0
        self.angle_error = 1
        #contact plates on the cone - like a button
        self.cone_button = 14  # pin

        self.object_array = [[1,0,2,3,4],[18,0,37,37,37]]
        self.previous_object = -1

        # Variables for spooling in/out the cable
        self.reset_cable_pul = 19 # pin Green wire
        self.reset_cable_dir = 6 # pin 31 Red wire
        self.reset_cable_en = 5 # pin 29 Blue wire (HIGH to Enable / LOW to Disable)
        self.reset_cable_speed = 0.00001  # default value

        self.spool_out_time_limit = 4.5  # seconds
        self.spool_in_time_limit = 12  # seconds
        self.object_moved = False # used for edge case if object didn't move during trial

        
        # hall effect sensor for rotating table
        self.hall_effect  = 15  # pin

        # Variables for turntable/encoder wheel
        self.turntable_motor_pwm = 4 # pin 7
        self.turntable_motor_in1 = 21 # pin 
        self.turntable_motor_in2 = 27 # pin 
        self.turntable_motor_en = 13  
        self.lower_arduino_reset_pin = 17

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
        self.turntable_pwm = gpio.PWM(self.turntable_motor_pwm, 1000)
        self.turntable_pwm.start(50)

        gpio.setup(self.hall_effect, gpio.IN)#, pull_up_down = gpio.PUD_DOWN)
        gpio.setup(self.cone_button, gpio.IN, pull_up_down = gpio.PUD_DOWN)

        # sets up the stepper motors
        self.reset_cone_motor = StepperMotor(self.reset_cone_pul, self.reset_cone_dir, self.reset_cone_en, self.reset_cone_speed)
        self.reset_cable_motor = StepperMotor(self.reset_cable_pul, self.reset_cable_dir, self.reset_cable_en, self.reset_cable_speed)
    #----------------------------------------------------------------------------------------------------------------------------#    

    def data_transfer(self, data):
        # need to rewrite once working on upper reset
        for num in data:
            if num == 0:
                self.send_transmission(6,self.I2C_SLAVE2_ADDRESS)
                var =  self.read_transmission(self.I2C_SLAVE2_ADDRESS)
                self.send_transmission(9,self.I2C_SLAVE2_ADDRESS)
                var =  self.read_transmission(self.I2C_SLAVE2_ADDRESS)
                self.send_transmission(7,self.I2C_SLAVE2_ADDRESS)
                var =  self.read_transmission(self.I2C_SLAVE2_ADDRESS)
            else:
                self.send_transmission(6,self.I2C_SLAVE2_ADDRESS)
                sleep(.01)
                var =  self.read_transmission(self.I2C_SLAVE2_ADDRESS)
                sleep(.01)
                self.send_transmission(num,self.I2C_SLAVE2_ADDRESS)
                sleep(.01)
                var =  self.read_transmission(self.I2C_SLAVE2_ADDRESS)
                sleep(.01)
                self.send_transmission(7,self.I2C_SLAVE2_ADDRESS)
                sleep(.01)
                var =  self.read_transmission(self.I2C_SLAVE2_ADDRESS)

    def send_swap_data(self, swap_list):
        # need to rewrite once working on upper reset
        b = self.object_array[0]
        c = b.index(swap_list[1])
        swap_list[1]=c
        for num in swap_list:
            self.send_transmission(10,self.I2C_SLAVE2_ADDRESS)
            var =  self.read_transmission(self.I2C_SLAVE2_ADDRESS)
            self.send_transmission((num+100),self.I2C_SLAVE2_ADDRESS)
            var =  self.read_transmission(self.I2C_SLAVE2_ADDRESS)
            self.send_transmission(11,self.I2C_SLAVE2_ADDRESS)
            var =  self.read_transmission(self.I2C_SLAVE2_ADDRESS)
        d = [self.object_array[0][0],self.object_array[1][0]]
        self.object_array[0][0] = self.object_array[0][c]
        self.object_array[1][0] = self.object_array[1][c]
        self.object_array[0][c] = d[0]
        self.object_array[1][c] = d[1]

    #----------------------------------------------------------------------------------------------------------------------------#    
    def testbed_reset(self):
        self.cone_reset_up()
        self.cable_reset_spool_in()
        sleep(.25)
        self.cable_reset_spool_out(self.spool_out_time_limit)
        self.cone_reset_down()
        self.turntable_reset_home()
        if self.goal_angle:
            self.turntable_move_angle(self.goal_angle)
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
        while True:
            button = self.lower_slave.get_data()
            if lift_time >= self.lift_time_limit or button == 1:
                if button == 1:  
                    print("button was pressed")
                else:
                    print("time ran out")
                break
            self.reset_cone_motor.move_for(0.01, self.reset_cone_motor.CCW)
            lift_time = time() - start_time
    #----------------------------------------------------------------------------------------------------------------------------#    
    def cone_reset_down(self, time_duration=None):
        print("cone down")
        if time_duration == None:
            time_duration = self.lower_time_limit
        start_time = time()
        lower_time = 0
        while True:
            if lower_time >= time_duration:
                break
            self.reset_cone_motor.move_for(0.01, self.reset_cone_motor.CW)
            lower_time = time() - start_time
    #----------------------------------------------------------------------------------------------------------------------------#    
    def cable_reset_spool_in(self):
        print("spool in")
        self.object_moved = False
        self.lower_slave.cone_button_mode()
        sleep(0.1)
        button_val = 0
        buffer = 0
        self.reset_cone_motor.override_enable()
        start_time = time()
        spool_in_time = 0
        while True:
            sleep(.01)
            button_val = self.lower_slave.get_data()
            if spool_in_time >= self.spool_in_time_limit or button_val == 1:
                if button_val == 1:
                    print("button was pressed")
                else:
                    print("time limit reached")
                break
            if buffer > 5:
                self.object_moved = True
            self.reset_cable_motor.move_for(0.025, self.reset_cable_motor.CCW)  # check rotations
            spool_in_time = time() - start_time
            buffer += 1 
        self.reset_cone_motor.override_disable()
    #----------------------------------------------------------------------------------------------------------------------------#    
    def cable_reset_spool_out(self, var):
        print("spool out")
        start_time = time()
        spool_out_time = 0
        while self.object_moved: # used as if statement as well
            if spool_out_time >= var:
                break
            self.reset_cable_motor.move_for(0.025, self.reset_cable_motor.CW)  # check rotations
            spool_out_time = time() - start_time
     #----------------------------------------------------------------------------------------------------------------------------#    
    def turntable_reset_home(self):
        print("resetting home")
        self.lower_slave.hall_effect_mode()
        sleep(0.1)
        hall_effect = self.lower_slave.get_data()
        if hall_effect == 0: 
            # already within HE range. To ensure rotation ends at beginning of range, turn for set degrees > range 
            print("Already within Home range, moving to guarantee front of range")
            gpio.output(self.turntable_motor_in1, gpio.LOW)
            gpio.output(self.turntable_motor_in2, gpio.HIGH)
            sleep(2.5) # let turntable move for 2.5 seconds

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
            if encoder_value >= goal_angle:
                gpio.output(self.turntable_motor_in1, gpio.LOW)
                gpio.output(self.turntable_motor_in2, gpio.LOW)
                print("angle motors stopped at: {}".format(encoder_value))
                break
        sleep(1) # make sure motors are fully stopped
        print("Angle recorded after motors stopped running: {}".format(self.lower_slave.get_data()))
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
    def object_swap(self, object_index):
        # need to rewrite once working on upper reset
        self.data_transfer(self.object_array[0])
        return_value = 0
        self.send_transmission(2,self.I2C_SLAVE2_ADDRESS)
        return_value = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
        self.send_transmission(3,self.I2C_SLAVE2_ADDRESS)
        self.send_transmission(3,self.I2C_SLAVE2_ADDRESS)

        while True:
            sleep(0.1) 
            self.send_transmission(3,self.I2C_SLAVE2_ADDRESS)
            return_value = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
            print(return_value)
            if return_value == 3:
                break
        print("Sending Lower Reset Code")
        self.cone_reset_up()
        self.cable_reset_spool_in()
        self.cone_reset_up()
        self.cable_reset_spool_out(.75)

        self.send_transmission(4,self.I2C_SLAVE2_ADDRESS)
        return_value = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
        sleep(4) 

        while True:
            sleep(0.1) 
            self.send_transmission(5,self.I2C_SLAVE2_ADDRESS)
            return_value = self.read_transmission(self.I2C_SLAVE2_ADDRESS)
            print(return_value)
            if return_value == 5:
                break

        self.cable_reset_spool_in()
        self.cone_reset_down()
        self.cable_reset_spool_out(self.spool_out_time_limit)
        self.turntable_reset_home()
#----------------------------------------------------------------------------------------------------------------------------#      
    def action_caller(self, object_index, goal_angle):
        if (self.previous_object == -1):
            # first run of testbed (assuming desired object is already on testbed)
            self.goal_angle = goal_angle
            # self.testbed_reset()
            self.previous_object = object_index
        elif not (object_index == self.previous_object):
            # different object
            self.send_swap_data([0,object_index])
            self.data_transfer(self.object_array[1])
            reset_testbed.object_swap(object_index)
            self.previous_object = object_index
            if not (goal_angle == 0):
                self.turntable_move_angle(goal_angle)
        else:
            # same object
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
What do you want to test? (enter the number)
""")


    reset_testbed = Testbed()
    if test_num == 0:
        reset_testbed.goal_angle = 30
        for i in range(45):
            sleep(3) # give me time to move object
            print("trial {}".format(i+1))
            reset_testbed.testbed_reset()

    elif test_num == 1:
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
    
    else:
        print("\nNot implemented\n")
#----------------------------------------------------------------------------------------------------------------------------#    
