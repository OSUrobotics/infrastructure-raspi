#!/usr/bin/env python2

import time
import spidev
import RPi.GPIO as gpio
import VL53L0X
from StepperMotor.stepper_motor import StepperMotor
from drawer_data import DataPoint

# Author: Ryan Roberts
#
# Class for controlling physical Drawer

class ResetException(Exception):
    """ Custom Exception to properly shut things down """
    def __init__(self, motor, message=""):
        motor.stop_motor()     
        gpio.cleanup()
        self.message = "{}\nGPIO cleaned up.".format(message)
        super().__init__(self.message)

class Drawer:
    def __init__(self):
        self.tof = VL53L0X.VL53L0X()
        self.tof.drawer_in_val = 331
        self.spi_lower = spidev.SpiDev()
        #spi_lower.open(1, 0) #seperate bus, can be used for multiprocessing
        self.spi_lower.open(0, 1) #same bus, synchronous
        self.spi_lower.max_speed_hz = 1000000
        self.spi_upper = spidev.SpiDev()
        self.spi_upper.open(0, 0)#bus for mcp3008 in charge of FSR's 8 - 12
        self.spi_upper.max_speed_hz = 1000000

        self.reset_pul = 5 #pin 29
        self.reset_dir = 6 # pin 31
        self.reset_en = 13    # pin 33, (High to Enable / LOW to Disable)
        self.reset_unwind_time = 1.5 # in seconds
        self.reset_speed = 0.0001 # seconds
        self.dis_buffer = 5 #buffer value for resetting drawer (in mm)
        self.fric_pul = 17 #pin 11
        self.fric_dir = 27 # pin 13
        self.fric_en = 22    # pin 15 (High to Enable / LOW to Disable)

        # TODO: Fix this part
        self.fric_steps = .000032 #relation between friction to # of motor steps
        self.fric_speed = .000001 #seconds
        self.fric_min_steps = 10000 #min steps it takes to get brake to touch drawer
        self.base_friction = 0.3 #minimum resistance drawer has (in kg)

        gpio.setmode(gpio.BCM) #sets pin mapping to GPIO pins
        gpio.setup(self.reset_pul, gpio.OUT)
        gpio.setup(self.reset_dir, gpio.OUT)
        gpio.setup(self.reset_en, gpio.OUT)
        gpio.setup(self.fric_pul, gpio.OUT)
        gpio.setup(self.fric_dir, gpio.OUT)
        gpio.setup(self.fric_en, gpio.OUT)
        
        self.reset_motor = StepperMotor(self.reset_pul, self.reset_dir, self.reset_en)
        self.fric_motor = StepperMotor(self.fric_pul, self.fric_dir, self.fric_en)
        self.__trial_data = []
        return
    

    def set_friction(self):
        # self.fric_motor.step(self.__resistance_steps, self.fric_motor.CW)
        self.fric_motor.override_enable() #keep motor resistance on
        return
    

    def reset_friction(self):
        # self.fric_motor.step(self.__resistance_steps, self.fric_motor.CCW)
        return
    

    def read_handle(self):
        data = [-1] * 14
        # lower ADC
        for chan in range(0,8):
            r = self.spi_lower.xfer2([1, 8 + chan << 4, 0])
            data[chan] = int(((r[1] & 3) << 8) + r[2])
        # spidev automatically switches CS signals
        # upper ADC
        for chan in range(0,4):
            r = self.spi_upper.xfer2([1, 8 + chan << 4, 0])
            data[chan + 8] = int(((r[1] & 3) << 8) + r[2])
        return data
 

    def start_new_trial(self, resistance, tof_mode = 0):
        self.tof_mode = tof_mode
        # self.__resistance_steps = int(((resistance - self.base_friction) / self.fric_steps) + self.fric_min_steps)
        
        self.tof.start_ranging(self.tof_mode)
        self.start_pos = self.tof.get_distance()
        self.set_friction()
        # self.__trial_data = [] #not need?
        return
    

    def collect_data(self):
        data_point = DataPoint(self.tof.get_distance() - self.start_pos, self.read_handle())
        return data_point
    

    def reset(self):
        # Reset friction motor
        self.reset_friction()

        # Wind in to pull in drawer
        # self.tof.start_ranging()
        self.reset_motor.start_motor(direction=self.reset_motor.CW, speed=self.reset_speed)
        try:
            while self.tof.get_distance() > self.tof.drawer_in_val:
                continue
        except Exception:
            raise ResetException(self.reset_motor)
        self.reset_motor.stop_motor()

        time.sleep(2)

        # Wind out to put slack in the line
        self.reset_motor.start_motor(direction=self.reset_motor.CCW, speed=self.reset_speed)
        try:
            time.sleep(self.reset_unwind_time)
        except Exception:
            raise ResetException(self.reset_motor)
        self.reset_motor.stop_motor()

        # Stop TOF
        self.tof.stop_ranging()
        return
        
        
    def get_trial_data(self):
        return self.__trial_data