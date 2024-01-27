#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Raphael KHORASSANI"
__status__ = "Development"

import numpy as np
import cv2
import rospy

from sensor_msgs.msg import Image as SensorImage
from std_msgs.msg import Bool
import time

class DetectColor:
    def __init__(self) :
        self.pub = rospy.Publisher("/is_auto_calibration_done", Bool, queue_size = 10)
        self.listener_init()

    def listener_init(self) :
        rospy.Subscriber("/do_an_auto_calibration", Bool, self.listener) 
        rospy.spin()

    def listener(self, value = True):
        self.color = rospy.get_param("/color_to_calibrate", default = "no_one")
        if self.color != "no_one" :
            self.subscriber = rospy.Subscriber("raw_image_data", SensorImage, self.callback_image)
        else : rospy.loginfo("Color is no_one")

    def callback_image(self, image_data) :
        h,w = image_data.height, image_data.width
        im = np.frombuffer(image_data.data, dtype = np.uint8)
        im = np.reshape(im, (h,w,3))

        H,W,c = im.shape
        wH = int(H * 0.2)
        wW = int(W * 0.4)

        zone_of_interest = im[(W - wW)//2 : (W-wW)//2 + wW, (H - wH)//2 : (H - wH)//2 + wH]

        values = np.median(zone_of_interest, axis = (0,1))

        param_name = "/red_RGB" if self.color == "red" else "/green_RGB"
        rospy.loginfo(param_name)

        rospy.set_param(param_name, values.astype(np.uint8).tolist())

        rospy.set_param("/color_to_calibrate", "no_one")

        rospy.loginfo(f"Calibration done for {self.color}")

        msg = Bool()
        msg.data = True

        self.pub.publish(msg)
        
        self.subscriber.unregister()

rospy.init_node("calibrate_color", anonymous = False)
detect_color = DetectColor()
