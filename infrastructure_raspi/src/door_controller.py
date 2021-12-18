#!/usr/bin/env python


# Main controller node
#
# door_controller.py
#
# Author: Ryan Roberts
#
# A node that handles all of the Action servers and topics for the Door

import rospy
import sys
import actionlib
import RPi.GPIO as gpio
from time import sleep
from door.door import Door

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
        self.stop_sleep_sub = rospy.Subscriber("start_data_collection/goal", StageActionGoal, self.stop_sleep_callback)
        self.start_sub = rospy.Subscriber("start_data_collection/result", StageActionResult, self.start_data_callback)
        self.stop_sub = rospy.Subscriber("stop_data_collection/result", StageActionResult, self.stop_data_callback)
        self.data_pub = rospy.Publisher("hardware_infsensor", DoorSensors, queue_size=10)
        self.rate = rospy.Rate(35)
        self.collect_data = False
        self.is_set = False
        
        while not rospy.is_shutdown():
            if(self.collect_data):
                #collect data
                data_message = DoorSensors()
                #format message. can be more optimized (and more feedback messages) if we integrate hardware class with controller
                data_point = self.hardware.collect_data()
                data_message.current_time = rospy.Time.now()
                data_message.tof = data_point.angle
                #computationally faster than using for loop with string concatenation
                data_message.fsr1 = data_point.handle_data[0]
                data_message.fsr2 = data_point.handle_data[1]
                data_message.fsr3 = data_point.handle_data[2]
                data_message.fsr4 = data_point.handle_data[3]
                data_message.fsr5 = data_point.handle_data[4]
                data_message.fsr6 = data_point.handle_data[5]
                data_message.fsr7 = data_point.handle_data[6]
                data_message.fsr8 = data_point.handle_data[7]
                data_message.fsr9 = data_point.handle_data[8]
                data_message.fsr10 = data_point.handle_data[9]
                data_message.fsr11 = data_point.handle_data[10]
                data_message.fsr12 = data_point.handle_data[11]
                data_message.fsr_contact_1 = data_point.handle_data[12]
                data_message.fsr_contact_2 = data_point.handle_data[13]
                self.data_pub.publish(data_message)
                self.rate.sleep()
                self.is_set = False
            else:
                if(not self.is_set):
                    sleep(2)
        #runs after ros is closed
        gpio.cleanup()

    def parameter_callback(self, goal):
        friction_setting = goal.parameters[0] * 100 #hack to get parameter to 100
        try:
            self.parameters_as.publish_feedback(TestParametersFeedback(status="setting friction to: {} N".format(friction_setting)))
            self.hardware.start_new_trial(friction_setting)
	    self.parameters_as.set_succeeded(TestParametersResult(result=0), text="SUCCESS")
        except:
	    self.parameters_as.set_aborted(TestParametersResult(result=100), text="FAILED")

    def reset_callback(self, goal):
        try:
	    self.reset_as.publish_feedback(StageFeedback(status="Resetting Drawer"))
            self.hardware.reset()
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
    door = Door()
    rospy.init_node("door_controller", argv=sys.argv)
    initialize = HardwareController(door)
