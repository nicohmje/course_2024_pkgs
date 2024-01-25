#!/usr/bin/env python3

import numpy as np
import rospy
import sys
import tf
from control_bolide.msg import SpeedDirection
from perception_bolide.msg import ForkSpeed
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point, Pose, Quaternion, Twist, Vector3

class odom_optical_fork:
    def __init__(self):
        self.pub = rospy.Publisher('Odom',Odometry,queue_size=10)
        self.Odom = Odometry()
        self.Odom_broadcaster = tf.TransformBroadcaster()
        self.L = 0.257 # Distance between location point and wheel point (back and front wheels) (m)
        self.fork = 0
        self.dir = 0

        self.current_time = rospy.Time.now()
        self.last_time =rospy.Time.now()

        self.x_pos = 0
        self.y_pos = 0
        self.theta_pos = 0
        self.dx = 0
        self.dy = 0
        self.dtheta =0

    def calcul_traction(self):     # From back wheel location
        self.current_time = rospy.Time.now()
        dt = (self.current_time - self.last_time).to_sec()
        # Angular update
        self.dtheta = self.fork*np.sin(self.dir)/self.L
        self.theta_pos += dt*self.dtheta

        # Linear update
        self.dx = self.fork*np.cos(self.theta_pos)*np.cos(self.dir)
        self.dy = self.fork*np.sin(self.theta_pos)*np.cos(self.dir)
        self.x_pos += dt*self.dx
        self.y_pos += dt*self.dy

        self.last_time = self.current_time

    def calcul_propulsion(self):   # From front wheel location
        self.current_time = rospy.Time.now()
        dt = (self.current_time - self.last_time).to_sec()
        # Angular update
        self.dtheta = self.fork*np.tan(self.dir)/self.L
        self.theta_pos += dt*self.dtheta

        # Linear update
        self.dx = self.fork*np.cos(self.theta_pos)
        self.dy = self.fork*np.sin(self.theta_pos)
        self.x_pos += dt*self.dx
        self.y_pos += dt*self.dy

        self.last_time = self.current_time

    def update(self):
        # Odom position
        Odom_quat = tf.transformations.quaternion_from_euler(0,0,self.theta_pos)
        self.Odom.pose.pose = Pose(Point(self.x_pos,self.y_pos,0.0),Quaternion(*Odom_quat))

        # Odom speed
        self.Odom.twist.twist = Twist(Vector3(self.dx,self.dy,0.0),Vector3(0.0,0.0,self.dtheta))

        # Transform
        self.Odom_broadcaster.sendTransform((self.x_pos,self.y_pos,0.0),Odom_quat,self.current_time,"base_link","odom")
        self.Odom.header.stamp = self.current_time
        self.Odom.header.frame_id = "odom"
        self.Odom.child_frame_id = "base_link"

        # Publish Topic
        self.pub.publish(self.Odom)
        
    def get_fork(self,msg:ForkSpeed):
        self.fork = msg.speed.data

    def get_dir(self,msg:SpeedDirection):
        self.dir = msg.direction*30*np.pi/180
        s.calcul_propulsion()
        s.update()


def listener(s:odom_optical_fork):
    rospy.Subscriber('raw_fork_data',ForkSpeed,s.get_fork)
    rospy.Subscriber('cmd_vel',SpeedDirection,s.get_dir)
    rospy.spin()   

if __name__ == '__main__' :
    rospy.init_node('fork_odom_process')
    s = odom_optical_fork()
    try : 
        listener(s)
    except (rospy.ROSInterruptException, KeyboardInterrupt) : sys.quit()