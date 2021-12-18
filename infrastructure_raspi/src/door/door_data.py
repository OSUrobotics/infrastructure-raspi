#!/usr/bin/env python

class DataPoint:
  def __init__(self, angle, handle):
    self.angle = angle
    self.handle_data = handle
  
  def __del__(self):
    del self.handle_data
