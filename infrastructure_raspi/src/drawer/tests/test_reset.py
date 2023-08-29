#!/usr/bin/env python2
"""
test_reset.py
Author: Luke Strohbehn

Simple file for testing an entire reset without the braking stepper motor

Notes for running this file:
        1. Start with the drawer pulled out. Make sure that the line from the spool to the drawer is relatively taut.
        2. Run script.
"""
import os, sys
__here__ = os.path.abspath(os.path.dirname(__file__))
parent_dir = __here__.strip("tests")
sys.path.append(parent_dir)

import RPi.GPIO as gpio
from StepperMotor.stepper_motor import StepperMotor
from VL53L0X import VL53L0X
import time

class ResetException(Exception):
    def __init__(self, motor, message):
        motor.stop_motor()     
        gpio.cleanup()
        self.message = "{}.\nGPIO cleaned up.".format(message)

        super().__init__(self.message)
    

def test_reset():
    _pul = 5 #pin 29
    _dir = 6 # pin 31
    _en = 13    # pin 33, (High to Enable / LOW to Disable)
    gpio.setmode(gpio.BCM) #sets pin mapping to GPIO pins
    gpio.setup(_pul, gpio.OUT)
    gpio.setup(_dir, gpio.OUT)
    gpio.setup(_en, gpio.OUT)

    print("Setting things up")
    time.sleep(2)

    # Start stepper
    motor = StepperMotor(_pul, _dir, _en)
    # Start TOF sensor
    tof = VL53L0X()
    tof.start_ranging()

    # Wind in to pull in drawer
    motor.start_motor(direction=motor.CW, speed = 0.0001)
    try:
        while tof.get_distance() > 331:
            continue
    except Exception:
        raise ResetException(motor)
    motor.stop_motor()

    time.sleep(2)
    
    # Wind out to put slack in the line
    motor.start_motor(direction=motor.CCW, speed = 0.0001)
    try:
        time.sleep(1.5)
    except Exception:
        raise ResetException(motor)
    motor.stop_motor()

    # Stop TOF
    tof.stop_ranging()
    return


def main():
	test_reset()
	gpio.cleanup()
	return


if __name__ == "__main__":
	main()