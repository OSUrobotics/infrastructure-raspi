#!/usr/bin/env/python3
"""
friction_test.py
Author: Luke Strohbehn
"""

from drawer import Drawer

drawer = Drawer()

try:
    drawer.start_new_trial(1)
    drawer.reset_friction()
except KeyboardInterrupt:
    drawer.fric_motor.stop_motor()
    drawer.stop_motors()