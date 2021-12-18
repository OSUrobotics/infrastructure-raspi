#!/usr/bin/env python

from time import time
import spidev
import RPi.GPIO as gpio
import VL53L0X
from stepper_motor import StepperMotor
from drawer_data import DataPoint

# Author: Ryan Roberts
#
# Class for controlling physical Drawer

class Drawer:

  def __init__(self):
    self.tof = VL53L0X.VL53L0X()
    self.spi_lower = spidev.SpiDev()
    #spi_lower.open(1, 0) #seperate bus, can be used for multiprocessing
    self.spi_lower.open(0, 1) #same bus, synchronous
    self.spi_lower.max_speed_hz = 1000000
    self.spi_upper = spidev.SpiDev()
    self.spi_upper.open(0, 0)#bus for mcp3008 in charge of FSR's 8 - 12
    self.spi_upper.max_speed_hz = 1000000

    self.reset_pul = 5 #pin 29
    self.reset_dir = 6 # pin 31 
    self.reset_en = 13  # pin 33, (High to Enable / LOW to Disable)
    self.time_unwind = 2 #in seconds
    self.reset_speed = .000001 # seconds
    self.dis_buffer = 5 #buffer value for resetting drawer (in mm)
    self.fric_pul = 17 #pin 11
    self.fric_dir = 27 # pin 13
    self.fric_en = 22  # pin 15 (High to Enable / LOW to Disable)
    self.fric_steps = .00032 #relation between friction to # of motor steps
    self.fric_speed = .000001 #seconds
    self.fric_min_steps = 2500 #min steps it takes to get brake to touch drawer
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
  
  def __set_friction(self):
    self.fric_motor.step(self.__resistance_steps, self.fric_motor.CW)
    gpio.output(self.fric_en, gpio.HIGH) #keep motor resistance on
  
  def __reset_friction(self):
    self.fric_motor.step_to(0)
    
  def __read_handle(self):
    data = [-1] * 14
    #lower ADC
    for chan in range(0,8):
      r = self.spi_lower.xfer2([1, 8 + chan << 4, 0])
      data[chan] = int(((r[1] & 3) << 8) + r[2])
    #spidev automatically switches CS signals
    #upper ADC
    for chan in range(0,4):
      r = self.spi_upper.xfer2([1, 8 + chan << 4, 0])
      data[chan + 8] = int(((r[1] & 3) << 8) + r[2])
    return data
 
  def start_new_trial(self, resistance, tof_mode = 0):
    self.tof_mode = tof_mode
    self.__resistance_steps = int(((resistance - self.base_friction) / self.fric_steps) + self.fric_min_steps)
    self.tof.start_ranging(self.tof_mode)
    self.start_pos = self.tof.get_distance()
    self.__set_friction()
    self.__trial_data = [] #not need?
  
  def collect_data(self):
    data_point = DataPoint(self.tof.get_distance() - self.start_pos, self.__read_handle())
    return data_point
  
  def reset(self):
    self.__reset_friction()
    did_move = False
    end_pos = self.start_pos + self.dis_buffer
    while (True):
      if(self.tof.get_distance() <= end_pos):
        break
      did_move = True
      self.reset_motor.move_for(0.1, self.reset_motor.CCW)
    if(did_move):
      self.reset_motor.move_for(self.time_unwind, self.reset_motor.CW)
    self.tof.stop_ranging()
    
  def get_trial_data(self):
    return self.__trial_data
    
  def __del__(self):
    gpio.cleanup()
    del self.__trial_data
