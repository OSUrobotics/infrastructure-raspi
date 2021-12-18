#!/usr/bin/env python


# Main controller node
#
# testbed_controller.py
#
# Author: Ryan Roberts
#
# A node that handles all of the Action servers and topics for the test bed

import rospy
import sys
import actionlib
import RPi.GPIO as gpio
from testbed.testbed_arduino import Testbed

#messages
from infrastructure_msgs.msg import TestParametersAction, TestParametersGoal, TestParametersFeedback, TestParametersResult
from infrastructure_msgs.msg import StageAction, StageGoal, StageFeedback, StageResult, StageActionResult, StageActionGoal

class HardwareController():

    def __init__(self, hardware):
        #action servers
        self.hardware = hardware
	self.parameters_as = actionlib.SimpleActionServer("set_test_parameters", TestParametersAction, self.parameter_callback, False) 
	self.parameters_as.start()
	self.reset_as = actionlib.SimpleActionServer("reset_hardware", StageAction, self.reset_callback, False) 
	self.reset_as.start()

    def parameter_callback(self, goal):
        reset_angle = goal.parameters[1]
        trial_object = goal.parameters[0]
        try:
            self.parameters_as.publish_feedback(TestParametersFeedback(status="setting object to: {}".format(trial_object)))
            #add testbed start trial call here
	    self.hardware.action_caller(trial_object, reset_angle)
	    self.parameters_as.set_succeeded(TestParametersResult(result=0), text="SUCCESS")
        except:
	    self.parameters_as.set_aborted(TestParametersResult(result=100), text="FAILED")

    def reset_callback(self, goal):
        try:
	    self.reset_as.publish_feedback(StageFeedback(status="Resetting Drawer"))
            self.hardware.testbed_reset()
	    self.reset_as.set_succeeded(StageResult(result=0), text="SUCCESS")
        except:
	    self.reset_as.set_aborted(StageResult(result=100), text="FAILED")


def cleanup_wrapper():
    gpio.cleanup()

if __name__ == "__main__":
    #initialize hardware
    testbed = Testbed()
    rospy.init_node("testbed_controller", argv=sys.argv)
    initialize = HardwareController(testbed)
    rospy.on_shutdown(gpio.cleanup)
    rospy.spin()
