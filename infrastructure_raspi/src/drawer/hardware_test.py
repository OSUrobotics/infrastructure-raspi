#!/usr/bin/env python
#
# Author: Ryan Roberts
#
# Testing code for Drawer

from drawer import Drawer
from time import time

if __name__ == "__main__":
  drawer = Drawer()
  while True:
    #testing UI
    trial_time = int(raw_input("Trial Time (seconds, -1 to quit): "))
    if(trial_time == -1):
      break
    tof_mode = int(raw_input("ToF mode (0 - 4): "))
    resistance = float(raw_input("Friction Resistance (kg): "))

    drawer.start_new_trial(resistance, tof_mode)
    timer = time() + trial_time
    while(time() <= timer):
      data_point = drawer.collect_data()
      print("ToF: {} -- FSR's: {} -- Time: {}".format(data_point.tof, data_point.handle_data, time()))
    drawer.reset()
  del drawer
