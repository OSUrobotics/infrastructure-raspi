#!/usr/bin/env python

class DataPoint:
  def __init__(self, tof, handle): #, time):
    self.tof = tof
    self.handle_data = handle
  
  def __del__(self):
    del self.handle_data
