#!/usr/bin/env python2
"""
test_reset.py
Author: Luke Strohbehn

Simple file for testing an entire reset without the braking stepper motor

Notes for running this file:
    1. Start with the drawer pulled out. Make sure that the line from the spool to the drawer is relatively taut.
    2. Run script.
"""

import RPi.GPIO as gpio
from StepperMotor.stepper_motor import StepperMotor
from VL53L0X import VL53L0X
import time

def test_reset():
  _pul = 5 #pin 29
  _dir = 6 # pin 31
  _en = 13  # pin 33, (High to Enable / LOW to Disable)
  gpio.setmode(gpio.BCM) #sets pin mapping to GPIO pins
  gpio.setup(_pul, gpio.OUT)
  gpio.setup(_dir, gpio.OUT)
  gpio.setup(_en, gpio.OUT)

  # Start stepper
  motor = StepperMotor(_pul, _dir, _en)
  # Start TOF sensor
  tof = VL53L0X()
  tof.start_ranging()

  motor.start_motor(direction=motor.CW, speed=0.0001)
  try:
    time.sleep(0.5)
  except KeyboardInterrupt:
    motor.stop_motor()
    gpio.cleanup()
    pass

  motor.stop_motor()
  gpio.cleanup()
  tof.stop_ranging()

  return


def main():
    test_reset()
    return


if __name__ == "__main__":
    main()