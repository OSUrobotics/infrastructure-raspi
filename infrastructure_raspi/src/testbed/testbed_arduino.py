#!/usr/bin/env python

#from os import DirEntry
from time import time, sleep
import RPi.GPIO as gpio
from stepper_motor import StepperMotor
import sys
import smbus2 as smbus#,smbus2

class Testbed():  # this is a test

    def __init__(self):
        
        # Slave Addresses
        self.I2C_SLAVE_ADDRESS = 15 #0x0b ou 11
        self.I2C_SLAVE2_ADDRESS = 14
        # Variables for moving cone up and down
        self.reset_cone_pul = 16 # pin
        self.reset_cone_dir = 20  # pin
        self.reset_cone_en = 12  # pin  (HIGH to Enable / LOW to Disable)
        self.reset_cone_speed = 0.00001 # default value

        
        
        self.lift_time_limit = 6.0  # seconds
        self.lower_time_limit = 2.0  # seconds
        self.goal_angle = 0
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
        self.spool_in_time_limit = 20  # seconds

        
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
        gpio.setup(self.lower_arduino_reset_pin, gpio.OUT)

        gpio.output(self.turntable_motor_en, gpio.HIGH)
        gpio.output(self.turntable_motor_in1, gpio.LOW)
        gpio.output(self.lower_arduino_reset_pin, gpio.HIGH)
        gpio.output(self.turntable_motor_in2, gpio.LOW)
        self.turntable_pwm = gpio.PWM(self.turntable_motor_pwm, 1000)
        self.turntable_pwm.start(50)

        gpio.setup(self.hall_effect, gpio.IN)#, pull_up_down = gpio.PUD_DOWN)
        gpio.setup(self.cone_button, gpio.IN, pull_up_down = gpio.PUD_DOWN)

        # sets up the stepper motors
        self.reset_cone_motor = StepperMotor(self.reset_cone_pul, self.reset_cone_dir, self.reset_cone_en, self.reset_cone_speed)
        self.reset_cable_motor = StepperMotor(self.reset_cable_pul, self.reset_cable_dir, self.reset_cable_en, self.reset_cable_speed)
    #----------------------------------------------------------------------------------------------------------------------------#       
    def send_transmission(self,val,address):
        self.I2Cbus = smbus.SMBus(1)
        with smbus.SMBus(1) as I2Cbus:
            while True:
                        try:
                            sleep(0.01)
                            self.I2Cbus.write_i2c_block_data(address, 0x00, [val])
                            sleep(0.01)
                            break
                        except:
                            sleep(.05)
                            self.I2Cbus.write_i2c_block_data(address, 0x00, [val])
                            sleep(.05)
    
    def read_transmission(self,address):
        self.I2Cbus = smbus.SMBus(1)
        with smbus.SMBus(1) as I2Cbus:
            while True:
                    try:
                        sleep(.01)
                        data=self.I2Cbus.read_byte_data(address,1)
                        return data
                    except:
                        sleep(.001)
    def data_transfer(self, data):
        self.I2Cbus = smbus.SMBus(1)
        with smbus.SMBus(1) as I2Cbus:
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
        self.I2Cbus = smbus.SMBus(1)
        with smbus.SMBus(1) as I2Cbus:
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
        self.lower_arduino_reset()
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
        self.I2Cbus = smbus.SMBus(1)
        with smbus.SMBus(1) as I2Cbus:
            if time_duration == None:
                time_duration = self.lift_time_limit
            start_time = time()
            lift_time = 0
            self.send_transmission(3,self.I2C_SLAVE_ADDRESS)
            while True:
                button = self.read_transmission(self.I2C_SLAVE_ADDRESS)
                if lift_time >= self.lift_time_limit or button == 1:
                    if button == 1:  
                        print("button was pressed")
                    else:
                        print("time ran out")
                    break
                self.reset_cone_motor.move_for(0.01, self.reset_cone_motor.CCW)
                lift_time = time() - start_time
    #----------------------------------------------------------------------------------------------------------------------------#    
    def cone_reset_down(self, time_duration=None):  # look at switching to steps moved
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
            start_time = time()
            spool_in_time = 0
            self.send_transmission(4,self.I2C_SLAVE_ADDRESS)
            button_val = 0
            while True:
                sleep(.01)
                button_val = self.read_transmission(self.I2C_SLAVE_ADDRESS)
                if spool_in_time >= self.spool_in_time_limit or button_val == 1:
                    if button_val == 1:
                        print("button was pressed")
                    else:
                        print("time limit reached")
                    break
                self.reset_cable_motor.move_for(0.025, self.reset_cable_motor.CCW)  # check rotations
                spool_in_time = time() - start_time        
    #----------------------------------------------------------------------------------------------------------------------------#    
    def cable_reset_spool_out(self, var):
        start_time = time()
        spool_out_time = 0
        while True:
            if spool_out_time >= var:
                break
            self.reset_cable_motor.move_for(0.025, self.reset_cable_motor.CW)  # check rotations
            spool_out_time = time() - start_time
     #----------------------------------------------------------------------------------------------------------------------------#    
    def turntable_reset_home(self):
        self.send_transmission(5,self.I2C_SLAVE_ADDRESS)
        sleep(.001)
        hall_effect = self.read_transmission(self.I2C_SLAVE_ADDRESS)
        gpio.output(self.turntable_motor_in1, gpio.LOW)
        gpio.output(self.turntable_motor_in2, gpio.HIGH)

        if hall_effect == 0:  # ensures that it goes to the proper home orientation.
            sleep(2)

        while True:
            hall_effect = self.read_transmission(self.I2C_SLAVE_ADDRESS)
            if hall_effect == 0:
                gpio.output(self.turntable_motor_in1, gpio.LOW)
                gpio.output(self.turntable_motor_in2, gpio.LOW)
                print("magnet detected")
                break
            sleep(0.01)
    #----------------------------------------------------------------------------------------------------------------------------#    
    def turntable_move_angle(self, goal_angle=20):      
        self.I2Cbus = smbus.SMBus(1)
        with smbus.SMBus(1) as I2Cbus:  
            self.lower_arduino_reset()
            self.send_transmission(2,self.I2C_SLAVE_ADDRESS)
            self.read_transmission(self.I2C_SLAVE_ADDRESS)
            self.send_transmission(6, self.I2C_SLAVE_ADDRESS)
            sleep(0.0001)
            gpio.output(self.turntable_motor_in1, gpio.LOW)
            gpio.output(self.turntable_motor_in2, gpio.HIGH)
            while True:
                    try:                    
                        first_byte =self.I2Cbus.read_byte_data(self.I2C_SLAVE_ADDRESS,1)
                        sleep(.01)
                        second_byte =self.I2Cbus.read_byte_data(self.I2C_SLAVE_ADDRESS,1)
                        encoder_value = (first_byte<< 8) + (second_byte)
                        print("recieve from slave:")
                        print(encoder_value)
                        sleep(.01)
                        if encoder_value >= goal_angle:
                            gpio.output(self.turntable_motor_in1, gpio.LOW)
                            gpio.output(self.turntable_motor_in2, gpio.LOW)
                            break
                    except:
                       #print("remote i/o error")
                        self.send_transmission(8, self.I2C_SLAVE_ADDRESS)
                        while True:
                            try:
                                sleep(.01)
                                self.I2Cbus.read_byte_data(self.I2C_SLAVE_ADDRESS,1)
                                sleep(.01)
                                break
                            except:
                                #print("remote i/o error")
                                sleep(.01)
                        while True:
                            try:
                                sleep(0.01)
                                self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [6])
                                sleep(.01)
                                break
                            except:
                                sleep(.01)
                                self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [6])
                                sleep(.01)
                        sleep(.1)
            sleep(.01)            
            self.send_transmission(7,self.I2C_SLAVE_ADDRESS)
            sleep(.01)
            self.read_transmission(self.I2C_SLAVE_ADDRESS)
            gpio.cleanup()
    #----------------------------------------------------------------------------------------------------------------------------#    
    def lower_arduino_reset(self):
        gpio.setup(self.lower_arduino_reset_pin, gpio.OUT)
        gpio.output(self.lower_arduino_reset_pin, gpio.LOW)
        sleep(.01)
        gpio.output(self.lower_arduino_reset_pin, gpio.HIGH)
        sleep(3)

    #----------------------------------------------------------------------------------------------------------------------------#
    def object_swap(self, object_index):
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
    # def get_user_params(self):
    #     repeat_bool = 1
    #     num_of_resets = 0
    #     current_action_list = []
    #     while repeat_bool:
    #         num_of_resets = 0
    #         num_of_degrees = 0
    #         swap_bool = 0
    #         first_object=0
    #         second_object=0

    #         num_of_resets = input("\nHow many resets would you like?\n")
    #         if num_of_resets != 0:
    #             num_of_degrees = input("\nHow many degrees would you like for each reset?\n")
    #         swap_bool = input("\nWould you like to swap objects? (1 for yes, 0 for no)\n")
    #         if swap_bool:
    #             first_object = input("\nWhich object would you like to grab first?\n")
    #             second_object = input("\nWhich object would you like to swap it with?\n")
    #         if num_of_resets != 0:
    #             print("\nYou have ", num_of_resets, "number of resets\n")
    #             print("\nAt an angle of ", num_of_degrees," degrees \n")
    #         else:
    #             print("\nYou have no resets\n")
    #         if swap_bool:
    #             print("\nAnd you have swaps between objects in location ", first_object, "and ", second_object, "\n")
    #         else:
    #             print("\nAnd no swaps\n")
    #         current_action = [num_of_resets,num_of_degrees,swap_bool,first_object,second_object]
    #         current_action_list.extend(current_action)
    #         repeat_bool = input("\nDo you have more actions? (1 for yes, 0 for no)\n")
    #     return current_action_list

#----------------------------------------------------------------------------------------------------------------------------#    
    def action_caller(self, object_index, goal_angle):
        self.current_reset_counter = 1

        #first time run of testbed
        if (self.previous_object == -1):
            self.goal_angle = 0
            self.testbed_reset()
            self.previous_object = object_index
        elif object_index != self.previous_object:
            self.send_swap_data([0,object_index])
            self.data_transfer(self.object_array[1])
            reset_testbed.object_swap(object_index)
            self.previous_object = object_index
            if goal_angle != 0:
                self.turntable_move_angle(goal_angle)
        else:
            self.goal_angle = goal_angle
            self.testbed_reset()
        print("\nfinished first call\n")
        return

#----------------------------------------------------------------------------------------------------------------------------#    
def on_exit(self, sig, func=None):
        gpio.cleanup()
        gpio.output(self.turntable_motor_in1, gpio.LOW)
        gpio.output(17, gpio.HIGH)
        gpio.output(self.turntable_motor_in2, gpio.LOW)
#----------------------------------------------------------------------------------------------------------------------------#    
if __name__ == '__main__':

    test_num = input("""
0) Resets or Swaps
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
        reset_testbed.action_caller(0,0)
        print("\nexited first call\n")
        #reset_testbed.action_caller(2,0)
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
