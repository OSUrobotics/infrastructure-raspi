#!/usr/bin/env python
#
# Author: Ryan Roberts
#
# script for testing electromagnet control with PWM pin 13

import RPi.GPIO as gpio
import sys
    
if __name__ == "__main__":
    freq = 200 #talk w/ UML about frequency setting
    pin = 13
    duty_cycle = float(sys.argv[1])
    gpio.setmode(gpio.BCM)
    gpio.setup(pin, gpio.OUT)
    pwm_pin = gpio.PWM(pin, freq)
    pwm_pin.start(duty_cycle)
    print("set DC to: {}".format(duty_cycle))
    try:
        while(True):
            duty_cycle = int(raw_input("Change DC to: "))
            pwm_pin.ChangeDutyCycle(duty_cycle)
    except:
        gpio.cleanup()
