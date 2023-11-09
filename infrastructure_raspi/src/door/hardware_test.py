#!/usr/bin/env python
#
# Author: Ryan Roberts

from door import Door
from time import time, sleep
import sys
import RPi.GPIO as gpio

if __name__ == "__main__":
   
    test = Door()
    resistance = int(raw_input("resistance (0 - 100): "))
    test.start_new_trial(resistance, True)
    print(sys.argv[1])
    if(int(sys.argv[1]) == 0):
        try:
            while True:
                d = test.collect_data()
                print("angle: {} ------ sensors: {}".format(d.angle, d.handle_data))
                sleep(.5)
        except KeyboardInterrupt:
            test.reset()
    elif(int(sys.argv[1]) == 1):
        test_time = float(sys.argv[2])
        timer = time() + test_time
        while (time() <= timer):
            print(test.collect_data().angle)
        test.reset()
    else:
        gpio.cleanup()
        raise Exception("Not valid first parameter")
    
