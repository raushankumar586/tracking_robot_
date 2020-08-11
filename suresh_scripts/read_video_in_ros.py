#!/usr/bin/env python

#copyright to Invento robotics
from datetime import datetime
import rospy
import sys 
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from datetime import datetime


class image_converter:

  def __init__(self):
    self.camera = "child.mp4"
    self.camera_topic = "/new_image_raw"
    self.image_pub = rospy.Publisher(self.camera_topic, Image)
    self.cap = cv2.VideoCapture(self.camera)
    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 3500)
    self.bridge = CvBridge()
    rospy.Timer(rospy.Duration(0.04), self.callback)

  def callback(self, data):
    try:
      success_frame, frame = self.cap.read()
      self.image_pub.publish(self.bridge.cv2_to_imgmsg(frame, "bgr8"))
      now = datetime.now()
      current_time = now.strftime("%H:%M:%S")
      print("current frame : {}, Current Time ;{}".format(self.cap.get(cv2.CAP_PROP_POS_FRAMES), current_time))
    except CvBridgeError as e:
      print(e)

def main(args):
  rospy.init_node('read_video_in_ros', anonymous=True)
  ic = image_converter()
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")


if __name__ == '__main__':
    main(sys.argv)
