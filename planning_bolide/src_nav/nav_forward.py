#!/usr/bin/env python3

__author__ = "Loris OUMBICHE and Raphael KHORASSANI"
__status__ = "Tested"
__version__ = "3.0.0"


#%% IMPORTS
import rospy
from control_bolide.msg import SpeedDirection
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
from nav_module.forward_functions import forward_3_dials, forward_n_dials

#%% CLASS
class NavForward():
    def __init__(self):
        
        # Initialize the node
        rospy.init_node("nav_forward", anonymous = True)

        # log info
        rospy.loginfo("Initializing the nav_forward node")

        # publisher
        self.pub = rospy.Publisher("cmd_vel",SpeedDirection,queue_size=10)

        # subscribers
        rospy.Subscriber('lidar_data',LaserScan,self.lidar_data_callback)
        rospy.Subscriber("/param_change_alert", Bool, self.get_all_params)



        self.cmd = SpeedDirection()
        self.navigation_dict = {
            "3Dials":forward_3_dials,
            "NDials":forward_n_dials
        }
        self.navigation_choice = "3Dials_spaced"

        self.get_all_params()
    
    def lidar_data_callback(self, msg:LaserScan):
        # Get the navigation function
        navigation_function = self.navigation_dict[self.navigation_choice]

        # Get the command
        self.cmd = navigation_function(
            lidar_data=msg,
            Kspeed=self.Kv,
            Kdir=self.Kd,
            Karg=self.Ka,
            mode=self.mode,
            n_dials=self.n_dials,
            FrontRatio = self.front_dial_ratio
        )

        # Publish the command
        self.pub.publish(self.cmd)

    def get_all_params(self, value = True):
        # Gains
        self.Kd = rospy.get_param("/gain_direction", default = 0.8)
        self.Kv = rospy.get_param("/gain_vitesse", default = 0.33)
        self.Ka = rospy.get_param("/gain_direction_arg_max", default = 0.2)

        navigation_mode = rospy.get_param("/navigation_mode", default = "3Dials_Classic")

        self.navigation_choice, self.mode = navigation_mode.split("_")

        self.feature = rospy.get_param("/navigation_feature", default = "mean")

        self.use_dials = rospy.get_param("/use_dials", default = False)
        self.n_dials = rospy.get_param("/navigation_n_dials", default = 11)
        self.front_dial_ratio = rospy.get_param("/front_dial_ratio", default = 0.1)
    


if __name__ == '__main__' :
    my_nav_lidar = NavForward()
    rospy.spin()
 

