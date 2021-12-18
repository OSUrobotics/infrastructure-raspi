#!/usr/bin/env python


# Template for a controller node
#
# door_controller.py
#
# Author: Ryan Roberts
#
# A node that handles all of the Action servers and topics for an apparatus

import rospy
import sys
import actionlib
import RPi.GPIO as gpio
from time import sleep
# import class that controls the hardware
from apparatus import ApparatusClass

#messages
from infrastructure_msgs.msg import TestParametersAction, TestParametersGoal, TestParametersFeedback, TestParametersResult
from infrastructure_msgs.msg import StageAction, StageGoal, StageFeedback, StageResult, StageActionResult, StageActionGoal
from infrastructure_msgs.msg import DoorSensors

class HardwareController():

    def __init__(self, hardware):
        #action servers
        self.hardware = hardware
	self.parameters_as = actionlib.SimpleActionServer("set_test_parameters", TestParametersAction, self.parameter_callback, False) 
	self.parameters_as.start()
	self.reset_as = actionlib.SimpleActionServer("reset_hardware", StageAction, self.reset_callback, False) 
	self.reset_as.start()
        # TEMPORARY SOLUTION (should be replaced with data_collection action server)
        # publisher that eavesdrops on data collection action server result topics and publishes to a topic
        # that gets recorded in a rosbag.
	# Include if you want to publish data from the apparatus: 
	
#         self.stop_sleep_sub = rospy.Subscriber("start_data_collection/goal", StageActionGoal, self.stop_sleep_callback)
#         self.start_sub = rospy.Subscriber("start_data_collection/result", StageActionResult, self.start_data_callback)
#         self.stop_sub = rospy.Subscriber("stop_data_collection/result", StageActionResult, self.stop_data_callback)
#         self.data_pub = rospy.Publisher("hardware_infsensor", DoorSensors, queue_size=10)
#         self.rate = rospy.Rate(35)
#         self.collect_data = False
#         self.is_set = False
        
        while not rospy.is_shutdown():
            if(self.collect_data):
                #collect data
                data_message = DoorSensors()
                #format message here
                self.data_pub.publish(data_message)
                self.rate.sleep()
                self.is_set = False
            else:
                if(not self.is_set):
                    sleep(2)
        #runs after ros is closed
        gpio.cleanup()

    def parameter_callback(self, goal):
        # goal.parameters includes trial parameters for the apparatus
        try:
            self.parameters_as.publish_feedback(TestParametersFeedback(status="Some status message"))
            # include any code for starting new trial here
	    self.parameters_as.set_succeeded(TestParametersResult(result=0), text="SUCCESS")
        except:
	    self.parameters_as.set_aborted(TestParametersResult(result=100), text="FAILED")

    def reset_callback(self, goal):
        try:
	    self.reset_as.publish_feedback(StageFeedback(status="Resetting Apparatus"))
            # include any code for resetting here
	    self.reset_as.set_succeeded(StageResult(result=0), text="SUCCESS")
        except:
	    self.reset_as.set_aborted(StageResult(result=100), text="FAILED")

    def stop_sleep_callback(self, msg):
        self.is_set = True

    def start_data_callback(self, msg):
        self.collect_data = True

    def stop_data_callback(self, msg):
        self.collect_data = False

if __name__ == "__main__":
    #initialize hardware
    app = ApparatusClass()
    rospy.init_node("hardware_controller", argv=sys.argv)
    initialize = HardwareController(app)
