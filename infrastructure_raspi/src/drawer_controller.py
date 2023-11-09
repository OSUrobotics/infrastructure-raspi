#!/usr/bin/env python


# Main controller node
#
# drawer_controller.py
#
# Author: Ryan Roberts
#
# A node that handles all of the Action servers and topics for the Drawer

import rospy
import sys
import actionlib
import os
import RPi.GPIO as gpio
from time import sleep
from drawer.drawer import Drawer
# from collections import deque

#messages
from infrastructure_msgs.msg import TestParametersAction, TestParametersGoal, TestParametersFeedback, TestParametersResult
from infrastructure_msgs.msg import StageAction, StageGoal, StageFeedback, StageResult, StageActionResult, StageActionGoal
from infrastructure_msgs.msg import DoorSensors

class HardwareController():
    def __init__(self, hardware):
        # action servers
        self.hardware = hardware
        self.parameters_as = actionlib.SimpleActionServer("set_test_parameters", TestParametersAction, self.parameter_callback, False) 
        self.parameters_as.start()
        self.reset_as = actionlib.SimpleActionServer("reset_hardware", StageAction, self.reset_callback, False) 
        self.reset_as.start()
        self.stop_sleep_sub = rospy.Subscriber("start_data_collection/goal", StageActionGoal, self.stop_sleep_callback)
        self.start_sub = rospy.Subscriber("start_data_collection/result", StageActionResult, self.start_data_callback)
        self.stop_sub = rospy.Subscriber("stop_data_collection/result", StageActionResult, self.stop_data_callback)
        self.data_pub = rospy.Publisher("hardware_infsensor", DoorSensors, queue_size=10)
        self.rate = rospy.Rate(35)
        self.collect_data = False
        self.is_set = False

        # self.timer = rospy.Timer(rospy.Duration(1/35), self.data_collection_callback)

        while not rospy.is_shutdown():
            if(self.collect_data):
                #collect data
                data_message = DoorSensors()
                #format message. can be more optimized (and more feedback messages) if we integrate hardware class with controller
                data_point = self.hardware.collect_data()
                data_message.current_time = rospy.Time.now()
                data_message.tof = data_point.tof
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
                data_message.fsr_contact_1 = -1
                data_message.fsr_contact_2 = -1
                self.data_pub.publish(data_message)
                # self.trial_data.append(data_message)
                self.rate.sleep()
                self.is_set = False
            else:
                if(not self.is_set):
                    sleep(2)
        # runs after node is closed
        gpio.cleanup()
        return


    def parameter_callback(self, goal):
        friction_setting = goal.parameters[0]
        try:
            self.parameters_as.publish_feedback(TestParametersFeedback(status="setting friction to: {} N".format(friction_setting)))
            self.hardware.start_new_trial(friction_setting)
            self.parameters_as.set_succeeded(TestParametersResult(result=0), text="SUCCESS")
        except:
            self.parameters_as.set_aborted(TestParametersResult(result=100), text="FAILED")
        return


    def reset_callback(self, goal):
        try:
            self.reset_as.publish_feedback(StageFeedback(status="Resetting Drawer"))
            self.hardware.reset()
            self.reset_as.set_succeeded(StageResult(result=0), text="SUCCESS")
        except Exception as e:
            print(e)
            self.reset_as.set_aborted(StageResult(result=100), text="FAILED")
        return


    def stop_sleep_callback(self, msg):
        self.is_set = True
        return


    def start_data_callback(self, msg):
        self.collect_data = True
        return


    def stop_data_callback(self, msg):
        self.collect_data = False
        return


def main():
    #initialize hardware
    drawer = Drawer()
    rospy.init_node("drawer_controller", argv=sys.argv)
    try:
        initialize = HardwareController(drawer)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    return


if __name__ == "__main__":
    main()
