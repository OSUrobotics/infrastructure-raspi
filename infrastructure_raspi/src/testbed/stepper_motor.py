#!/usr/bin/env python
from time import time, sleep
import RPi.GPIO as gpio
import numpy as np

# Author: Ryan Roberts
#
#TODO:
# add resolution parameter (pulse/rev) to do movements given angles

class StepperMotor:
  """
  A class used to run a stepper motor with a motor controller
  on a Raspberry Pi
  
  ...
  
  Attributes
  ----------
  CCW : int
    describes the counterclockwise direction of stepper motor (default 1)
  CW : int
    describes the clockwise direction of stepper motor (default 0)
  pulse_pin : int
    GPIO pin number for pulse pin of stepper motor controller
  dir_pin : int
    GPIO pin number for direction pin of stepper motor controller
  en_pin : int
    GPIO pin number for enable pin of stepper motor controller
  default_speed : float
    delay between pulses in seconds / 2 (default .000001)
  current_steps : int
    step count of stepper motor relative to its zero position
  
  Methods
  -------
  move_for(run_time, direction, speed = None):
    moves motor in a single direction for a given time
  step(num_steps, direction, speed = None):
    steps motor in a single direction for a given amount of steps
  step_to(step_target, speed = None):
    steps motor to a specific step relative to its zero positon
  get_current_steps():
    returns current step position of motor
  override_position(step_value):
    overrides the current step value of motor.
  override_enable():
    force enable motor
  override_disable():
    force disables motor
  """
  
  CCW = 1
  CW = 0

  def __init__(self, pulse_pin, dir_pin, en_pin, default_speed = None):
    """
    Constructor
    
    Parameters
    ----------
    pulse_pin : int
      GPIO pin number for pulse pin of stepper motor controller
    dir_pin : int
      GPIO pin number for direction pin of stepper motor controller
    en_pin : int
      GPIO pin number for enable pin of stepper motor controller
    default_speed : float, optional
      delay between pulses in seconds / 2 (default .000001)
    """
    
    if(default_speed == None):
      default_speed = .000001
    try:
      self.pulse_pin = int(pulse_pin)
      self.dir_pin = int(dir_pin)
      self.en_pin = int(en_pin)
    except ValueError:
      print("Invalid pin values")
      return
    except Exception as e:
      print(e)
      return
    except:
      print("Unknown error during pin assignments")
      return
    try:
      self.default_speed = float(default_speed)
    except ValueError:
      print("Invalid speed value")
      return
    except Exception as e:
      print(e)
      return
    except:
      print("Unknown error during speed assignment")
      return
    self.__current_steps = 0
  
  def move_for(self, run_time, direction, speed = None):
    """
    Moves motor in a single direction for a given time.
    Note: number of steps made by motor may vary using this method.
    Do not use for precise movements
    
    Parameters
    ----------
    run_time : float
      time in seconds for motor to run
    direction : int
      direction for motor to move in. Highly suggest using CW and CCW
      class variables
    speed : float, optional
      delay between pulses in seconds / 2 (default default_speed)
      
    Returns
    -------
    None
    """
    
    if(speed == None):
      speed = self.default_speed
    try:
      gpio.output(self.dir_pin, direction)
      gpio.output(self.en_pin, gpio.HIGH)
    except Exception as e:
      print("Motor pins not configured properly. Error: {}".format(e))
      return
    except:
      print("Unknown error during controlling motor pins")
      return
    inc = 0
    if(direction==self.CW):
      inc = 1
    elif(direction==self.CCW):
      inc = -1
    else:
      raise Exception("Invalid direction. Direction does not match CW or CCW direction of motor")
      return
    timer = time() + run_time
    try:
      while(time() <= timer):
        gpio.output(self.pulse_pin, gpio.HIGH)
        sleep(speed)
        gpio.output(self.pulse_pin, gpio.LOW)
        sleep(speed)
        self.__current_steps += inc
      gpio.output(self.en_pin, gpio.LOW)
    except ValueError:
      print("Invalid speed value")
      return
    except Exception as e:
      print(e)
      return
    except:
      print("Unknown error during motor stepping")
      return
  
  def step(self, num_steps, direction, speed = None):
    """
    Steps motor in a single direction for a given amount of steps
    
    Parameters
    ----------
    num_steps : int
      number of steps to move motor
    direction : int
      direction for motor to move in. Highly suggest using CW and CCW
      class variables
    speed : float, optional
      delay between pulses in seconds / 2 (default default_speed)
      
    Returns
    -------
    None
    """
    
    if(speed == None):
      speed = self.default_speed
    try:
      gpio.output(self.dir_pin, direction)
      gpio.output(self.en_pin, gpio.HIGH)
    except Exception as e:
      print("Motor pins not configured properly. Error: {}".format(e))
      return
    except:
      print("Unknown error during controlling motor pins")
      return
    try:
      if(direction==self.CW):
        self.__current_steps += int(num_steps)
      elif(direction==self.CCW):
        self.__current_steps -= int(num_steps)
      else:
        raise Exception("Invalid direction. Direction does not match CW or CCW direction of motor")
        return
    except ValueError:
      print("invalid num_steps assignment")
      return
    except Exception as e:
      print(e)
      return
    except:
      print("Unknown error during adding num_steps to current steps of motor")
      return  
    try:
      for steps in range(int(num_steps)):
        gpio.output(self.pulse_pin, gpio.HIGH)
        sleep(speed)
        gpio.output(self.pulse_pin, gpio.LOW)
        sleep(speed)
      gpio.output(self.en_pin, gpio.LOW)
    except ValueError:
      print("Invalid speed value")
      return
    except Exception as e:
      print(e)
      return
    except:
      print("Unknown error during motor stepping")
      return   
    
  def step_to(self, step_target, speed = None):
    """
    Steps motor to a specific step relative to its zero positon
    
    Parameters
    ----------
    step_target : int
      target step position to move motor to
    speed : float, optional
      delay between pulses in seconds / 2 (default default_speed)
      
    Returns
    -------
    None
    """
    
    if(speed == None):
      speed = self.default_speed
    try:
      num_steps = int(step_target) - self.__current_steps
      if(num_steps >= 0):
        self.step(abs(num_steps), self.CW, speed)
      else:
        self.step(abs(num_steps), self.CCW, speed)
      self.__current_steps = step_target
    except ValueError:
      print("Invalid step target")
      return
    except Exception as e:
      print(e)
      return
    except:
      print("Unknown error")
      return
  
  def get_current_steps(self):
    """
    Returns current step position of motor.
    Negative steps = CCW direction
    Positive steps = CW direction
    
    Parameters
    ----------
    None
      
    Returns
    -------
    int
    """
    
    return self.__current_steps
  
  def override_position(self, step_value):
    """
    overides the current step value of motor.
    NOTE: motor does not move to new step value. Use
    the step_to() method to move motor to a absolute step
    position.
    
    Parameters
    ----------
    step_value : int
      new value of the current step position of motor
      
    Returns
    -------
    None
    """
    
    try:
      self.__current_steps = int(step_value)
    except ValueError:
      print("Invalid new step position")

  def override_enable(self):
    """
    force enables motor. This should NOT be used to
    control motor movement. Enabling/disabling of motors is handled
    internally by move methods
    
    Parameters
    ----------
    NONE
      
    Returns
    -------
    None
    """
    try:
      gpio.output(self.en_pin, gpio.HIGH)
    except Exception as e:
      print("Motor pins not configured properly. Error: {}".format(e))
    except:
      print("Unknown error during enabling motor")
    
  def override_disable(self):
    """
    force disables motor. This should NOT be used to
    control motor movement. Enabling/disabling of motor is handled
    internally by move methods
    
    Parameters
    ----------
    NONE
      
    Returns
    -------
    None
    """
    
    try:
      gpio.output(self.en_pin, gpio.LOW)
    except Exception as e:
      print("Motor pins not configured properly. Error: {}".format(e))
    except:
      print("Unknown error during disabling motor")
