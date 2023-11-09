#!/usr/bin/env python
#
# Author: Kyle DuFrene

import RPi.GPIO as GPIO
import sys
from time import sleep
    
if __name__ == "__main__":
    pin = 13
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    try:
        while(True):
            GPIO.output(pin, 1)
            sleep(2)
            GPIO.output(pin, 0)
            sleep(2)
    except:
        GPIO.cleanup()
