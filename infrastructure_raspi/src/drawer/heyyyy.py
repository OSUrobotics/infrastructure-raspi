#!/usr/bin/env python

from time import sleep
import spidev
import RPi.GPIO as gpio
import VL53L0X
from StepperMotor.stepper_motor import StepperMotor
from drawer_data import DataPoint

# Author: Ryan Roberts
#
# Class for controlling physical Drawer


reset_pul = 17 #pin 29
reset_dir = 27 # pin 31
reset_en = 22  # pin 33, (High to Enable / LOW to Disable)
gpio.setmode(gpio.BCM) #sets pin mapping to GPIO pins
gpio.setup(reset_pul, gpio.OUT)
gpio.setup(reset_dir, gpio.OUT)
gpio.setup(reset_en, gpio.OUT)

try:
	reset_motor = StepperMotor(reset_pul, reset_dir, reset_en)


	reset_motor.start_motor(reset_motor.CCW)
	sleep(5000)

	reset_motor.stop_motor()
	#reset_motor.move_for(time_unwind, reset_motor.CW)
 
except KeyboardInterrupt:
	print("cleanup")
	gpio.cleanup()