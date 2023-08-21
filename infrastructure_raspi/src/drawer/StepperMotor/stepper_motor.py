#!/usr/bin/env python2
from time import time, sleep
import RPi.GPIO as gpio
import numpy as np
import os, signal, threading, ctypes

# Author: Ryan Roberts
# Email : roberyan@oregonstate.edu
# Date  : 5/2022

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
  
  Methods
  -------
  move_for(run_time, direction, speed = None):
    moves motor in a single direction for a given time

  step(num_steps, direction, speed = None):start_motor
  start_motor():
    starts motor in a given direction indefinitely

  is_running():
    returns True if motor is running, False otherwise
  """
  
  CCW = 1
  CW = 0

  # setting a signal handler for current process for SIGUSR2 signal
  def __handle_SIGUSR2(self, sig, frame):
    os._exit(os.EX_OK)

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
      default_speed = 0.0001 #0.0001
    try:
      self.pulse_pin = int(pulse_pin)
      self.dir_pin = int(dir_pin)
      self.en_pin = int(en_pin)
    except ValueError:
      raise ValueError("Invalid pin values")
    except Exception as e:
      raise Exception(e)
    try:
      self.default_speed = float(default_speed)
    except ValueError:
      raise ValueError("Invalid speed value")
    except Exception as e:
      raise Exception(e)

    # child PID retrieved from fork().
    # When no child process is running, value is -5
    signal.signal(signal.SIGUSR2, self.__handle_SIGUSR2)
    self.__child_pid = -5
  
  def move_for(self, run_time, direction, speed = None):
    """
    Blocking. Moves motor in a single direction for a given time.
    
    Do not need to call stop_motor() after running this method.

    Note: Number of steps made by motor may vary using this method.
          Do not use for precise movements.
    
    Parameters
    ----------
    run_time : float
      time in seconds for motor to run
    direction : int
      direction for motor to move in. Highly suggest using CW and CCW
      class variables
    speed : float, optional
      delay between pulses in seconds / 2 (default = self.default_speed)
      
    Returns
    -------
    None
    """
    timer = time() + run_time
    self.start_motor(direction, speed)
    while(time() <= timer):
      continue
    self.stop_motor()
  
  def step(self, num_steps, direction, speed = None):
    """
    Blocking. Steps motor in a single direction for a given amount of steps.

    Do not need to call stop_motor() after running this method.
    
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
    if self.is_running():
        # A child process has already been spawned
        raise Exception("Motor already running. Call stop_motor() first")
    if(speed == None):
        speed = self.default_speed
    try:
        gpio.output(self.dir_pin, direction)
        gpio.output(self.en_pin, gpio.HIGH)
    except Exception as e:
        raise Exception("Motor pins not configured properly. Error: {}".format(e))
    self.__child_pid = os.fork()
    if self.__child_pid == 0:
        # child process, step motor num_steps times
        for steps in range(int(num_steps)):
          gpio.output(self.pulse_pin, gpio.HIGH)
          sleep(speed)
          gpio.output(self.pulse_pin, gpio.LOW)
          sleep(speed)
        os._exit(os.EX_OK)
    else:
        # parent process, wait for child process to finish
        return_status = os.waitpid(self.__child_pid, 0)
        if not os.WIFEXITED(return_status[1]):
          raise Exception("Failed to step motor for entire amount. Stop Signal: {}".format(os.WSTOPSIG(return_status)))
        # put motor in stopped state
        self.__child_pid = -5
        gpio.output(self.en_pin, gpio.LOW)

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
      raise Exception("Motor pins not configured properly. Error: {}".format(e))
    
  def override_disable(self):
    """
    force disables motor. This should NOT be used to
    control motor movement. Enabling/disabling of motor is handled
    internally by move methods
    
    ParametersException
    ----------
      NONE
      
    Returns
    -------
      None
    """
    
    try:
      gpio.output(self.en_pin, gpio.LOW)
    except Exception as e:
      raise Exception("Motor pins not configured properly. Error: {}".format(e))

  def is_running(self):
    """
    returns True if motor is running, False otherwise
    """
    return False if self.__child_pid == -5 else True

  def stop_motor(self):
    """
    Stops motor. Raises Exception if no motor is currently running
    
    Parameters
    ----------
      NONE
      
    Returns
    -------
      None
    """
    # kills motor process using custom signal SIGUSR2 UNIX signal.
    if not self.is_running():
      raise Exception("No motor to kill")
    os.kill(self.__child_pid, signal.SIGUSR2)
    self.__child_pid = -5
    gpio.output(self.en_pin, gpio.LOW)

  def start_motor(self, direction, speed = None):
    """
    Starts motor in a given direction indefinitely. Non-blocking. 
    Raises Exception if motor is currently running. Call stop_motor() to stop the motor
    
    Parameters
    ----------
      NONE
      
    Returns
    -------
      None
    """
    # runs motor indefinitely. Non-blocking
    if self.is_running():
        # A child process has already been spawned
        raise Exception("Motor already running. Call stop_motor() first")
    if(speed == None):
      speed = self.default_speed
    
    try:
      gpio.output(self.dir_pin, direction)
      gpio.output(self.en_pin, gpio.HIGH)
    except Exception as e:
      raise Exception("Motor pins not configured properly. Error: {}".format(e))
    self.__child_pid = os.fork()
    if self.__child_pid == 0:
        # child process, run motor indefinitely
      while True:
        gpio.output(self.pulse_pin, gpio.HIGH)
        sleep(speed)
        gpio.output(self.pulse_pin, gpio.LOW)
        sleep(speed)
    else:
      # parent process, wait no hang for child process so it becomes a zombie. 
      # (child should never return anyways)
        #  Relevant: https://www.youtube.com/watch?v=JghkG4WydNk
      os.waitpid(self.__child_pid, os.WNOHANG)
