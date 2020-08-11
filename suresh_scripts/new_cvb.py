#!/usr/bin/env python
import numpy as np
import roslib
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

start = False

class tracker:
    
    def __init__(self):
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("/new_image_raw", Image, self.callback)
        self.mog = cv2.createBackgroundSubtractorMOG2();    


    def callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        self.frame_width = cv_image.shape[0]
        self.frame_height = cv_image.shape[1]

        global start, frame1, frame2
        if not start:
			frame1 = cv_image
			frame2 = cv_image
			print("start...")
			start = True
        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        crop_img = gray[150:300, 200:500]
        median_blur5 = cv2.medianBlur(gray, 5)
        median_blur11 = cv2.medianBlur(gray, 11)

        subtract_gray5 = self.mog.apply(median_blur5); 
        subtract_gray11 = self.mog.apply(median_blur11); 
        subtract_gray2 = self.mog.apply(gray); 

        # print("size : {}".format(gray.shape))
        # blur = cv2.GaussianBlur(subtract_gray,(11,11), 0)
        blur = cv2.medianBlur(subtract_gray5, 5)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        _, thresh40 = cv2.threshold(blur, 254, 255, cv2.THRESH_BINARY)
        erosion = cv2.erode(thresh,None, iterations=3)
        dialation_after_erosion = cv2.erode(erosion,None, iterations=3)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dialation_after_erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)      

        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            if area > 900 and area < 10000:
                # print("Area : {}".format(cv2.contourArea(contour)))
                cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)
        image = cv2.resize(frame1, (1280,720))
        # cv2.imshow("feed", thresh)

        # cv2.imshow("feed", gray)
        # cv2.imshow("diff", diff)
        cv2.imshow("image", image)
        # cv2.imshow("erosion", erosion)
        cv2.imshow("dialation_after_erosion", dialation_after_erosion)
        
        frame1 = frame2
        frame2 = cv_image
        cv2.waitKey(1)

def main(args):
    ic = tracker()
    rospy.init_node('tracker', anonymous=True)
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)



