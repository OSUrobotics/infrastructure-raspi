#!/usr/bin/env/python3
"""
friction_test.py
Author: Luke Strohbehn
"""
import RPi.GPIO as gpio
from drawer import Drawer
import time

drawer = Drawer()

sleep_time = 10

def main():
    try:
        # Set the friction
        print("Starting friction motor test")
        drawer.start_new_trial(resistance=2.0)

        # Sleep
        print("Resetting friction motor in {} seconds.".format(sleep_time))
        time.sleep(sleep_time)

        # Reset friction
        drawer.reset_friction()
        print("Done.")

    except KeyboardInterrupt:
        drawer.fric_motor.stop_motor()
        drawer.stop_motors()
    return


if __name__ == "__main__":
    main()
    gpio.cleanup()