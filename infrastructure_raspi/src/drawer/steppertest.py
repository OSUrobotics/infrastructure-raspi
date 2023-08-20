#!/usr/bin/env python2

import RPi.GPIO as gpio
from StepperMotor.stepper_motor import StepperMotor
import time

def test_fric_motor():
  _pul = 17 #pin 29
  _dir = 27 # pin 31
  _en = 22  # pin 33, (High to Enable / LOW to Disable)
  gpio.setmode(gpio.BCM) #sets pin mapping to GPIO pins
  gpio.setup(_pul, gpio.OUT)
  gpio.setup(_dir, gpio.OUT)
  gpio.setup(_en, gpio.OUT)

  motor = StepperMotor(_pul, _dir, _en)

  try:
    motor.step(
      num_steps=5000,
      direction=motor.CW
    )
  except KeyboardInterrupt:
    motor.stop_motor()
    gpio.cleanup()
    pass

  return


def test_reset_motor():
  _pul = 5 #pin 29
  _dir = 6 # pin 31
  _en = 13  # pin 33, (High to Enable / LOW to Disable)
  gpio.setmode(gpio.BCM) #sets pin mapping to GPIO pins
  gpio.setup(_pul, gpio.OUT)
  gpio.setup(_dir, gpio.OUT)
  gpio.setup(_en, gpio.OUT)

  # Start stepper
  motor = StepperMotor(_pul, _dir, _en)

  motor.start_motor(direction=motor.CCW, speed=0.0001)
  try:
    time.sleep(1.5)
  except KeyboardInterrupt:
    motor.stop_motor()
    gpio.cleanup()
    pass

  motor.stop_motor()
  gpio.cleanup()

  return


def main():
  # test_fric_motor()
  test_reset_motor()
  return

if __name__ == "__main__":
  main()