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
    duty_cycle = float(sys.argv[1])
    gpio.setmode(gpio.BCM)
    gpio.setup(in3, gpio.OUT)
    gpio.setup(in4, gpio.OUT)
    gpio.setup(enB, gpio.OUT)
    gpio.output(in3, 0)
    gpio.output(in4, 0)
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
