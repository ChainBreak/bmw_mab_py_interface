#! /usr/bin/env python2

import time
import rospy
import std_msgs.msg
from BmwMabInterface import bmwMabInterface

class ConeSteering():
    def __init__(self):
        rospy.init_node("cone_steering")
        rospy.Subscriber("steering_angle", std_msgs.msg.Float32, self.callback_steering_angle)
        
        self.angle = 0.0
        self.smooth_angle = 0.0
        self.smooth_alpha = 0.1
        self.loop()
        
    def loop(self):
        rate = rospy.Rate(30)
        
        with bmwMabInterface.BmwMabInterface() as bmw:
        
            while not rospy.is_shutdown():
                self.smooth_angle += self.smooth_alpha * ( self.angle - self.smooth_angle)
                
                bmw.setCarData("ref_steering_angle", self.smooth_angle)
                rate.sleep()
            
             
    def callback_steering_angle(self,data):
        self.angle = data.data
        


if __name__ == "__main__":
    print("hello")
    ConeSteering()
