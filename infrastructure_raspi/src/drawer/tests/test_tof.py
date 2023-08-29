#!/usr/bin/env python2
"""
test_tof.py
Author: Luke Strohbehn

A simple testing of the time of flight sensor.
"""

from VL53L0X import VL53L0X
import time

def test_tof():
    print("Starting TOF test...")
    tof = VL53L0X()
    
    # tof.open()
    # tof.get_timing()
    tof.start_ranging(mode=0)
    start_time = time.time()

    while (time.time() - start_time) < 5:
        dist = tof.get_distance()
        print(dist)
        time.sleep(0.001)

    tof.stop_ranging()

    return


if __name__ == "__main__":
    test_tof()