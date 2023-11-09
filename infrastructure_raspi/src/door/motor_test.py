#!/usr/bin/env python
#
# Author: Ryan Roberts

import RPi.GPIO as gpio
import sys
from time import sleep, time

if __name__ == "__main__":
    # 25 or 20 are good duty cycles
    in3 = 4
    in4 = 5
    enB = 12
    freq = 100
    
    
    
    try:
        duty_cycle = float(sys.argv[1])
        gpio.setmode(gpio.BCM)
        gpio.setup(in3, gpio.OUT)
        gpio.setup(in4, gpio.OUT)
        gpio.setup(enB, gpio.OUT)
        reset_pwm = gpio.PWM(enB, freq)
        reset_pwm.start(duty_cycle)
        print("Dir 1")
        #gpio.output(enB, 1)
        gpio.output(in3, 0)
        gpio.output(in4, 1)
        sleep(1)
        print("Dir 2")
        gpio.output(in3, 1)
        gpio.output(in4, 0)
        #gpio.output(enB, 1)
        sleep(1)
        gpio.output(in3, 0)
        gpio.output(in4, 0)
        #gpio.output(enB, 0)
    
    except KeyboardInterrupt:
        gpio.cleanup()
    gpio.cleanup()
    exit()
    
    pwm_pin = gpio.PWM(enB, freq)
    print("starting at DC {}".format(duty_cycle))
    pwm_pin.start(duty_cycle)
    try:
        while(True):
            print("10")
            #unwind
            gpio.output(in3, 1)
            gpio.output(in4, 0)
            sleep(1)
            print("01")
            #wind
            gpio.output(in3, 0)
            gpio.output(in4, 1)
            sleep(1)
            print("00")
            #stop
            gpio.output(in3, 0)
            gpio.output(in4, 0)
            sleep(3)
    except KeyboardInterrupt:
        gpio.cleanup()
