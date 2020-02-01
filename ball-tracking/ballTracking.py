from collections import deque
from imutils.video import VideoStream
import numpy as np
import cv2
import imutils
import time
import json

def getBallColorParameters():
    hue = [0,255]
    sat = [0,255]
    val = [0,255]
    try:
        with open('/home/bertone/Documents/Coding/PiCam-FRC-1860-2020/ball-tracking/distanceParameters.json', 'r') as f:
            parameters_dict = json.load(f)
        hue = parameters_dict['hue']
        sat = parameters_dict['sat']
        val = parameters_dict['val']
    except:
        print("Error ball color parameters")
    return hue, sat, val

# construct the argument parse and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-v", "--video",
# 	help="path to the (optional) video file")
# ap.add_argument("-b", "--buffer", type=int, default=64,
# 	help="max buffer size")
# args = vars(ap.parse_args())

# pts = deque(maxlen=args["buffer"])

# if not args.get("video", False):
# cap = cv2.VideoCapture(0)

# cap.set(3, 360)
# cap.set(4, 270)
# cap.set(cv2.CAP_PROP_GAIN, 0.3 )

# else:
# 	cap = cv2.VideoCapture(args["video"])

time.sleep(2.0)

def findBall(imageFrame):
	frame = imageFrame
	frame = cv2.resize(frame, (int(frame.shape[1]*.4), int(frame.shape[0]*.4)))
	# blurred = cv2.GaussianBlur(frame, (11, 11), 0)

	kernel = np.ones((15,15),np.float32)/225
	blurred = cv2.filter2D(frame,-1,kernel)

	cv2.imshow("CONVOLUTION", blurred)

	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	hue, sat, val = getBallColorParameters()
	mask = cv2.inRange(hsv, (hue[0], sat[0], val[0]),  (hue[1], sat[1], val[1]))
	mask = cv2.erode(mask, None, iterations=5)
	mask = cv2.dilate(mask, None, iterations=3)

	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
	opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=8)

	cv2.imshow("Opening", opening)

	cnts = cv2.findContours(opening.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = None

	if len(cnts) > 0:
		for i in range(len(cnts)):
			approx = cv2.approxPolyDP(cnts[i],0.01*cv2.arcLength(cnts[i],True),True)
			contourArea = cv2.contourArea(cnts[i])
			print("CA: ",contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(cnts[i])
			minEnclosingCircleArea = np.pi*radius**2
			print("MIN: ", minEnclosingCircleArea)
			areaRatio = contourArea/(minEnclosingCircleArea)
			if 0.65<areaRatio and areaRatio<1.35:
				if radius>15:
					M = cv2.moments(cnts[i])
					center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
					cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
					cv2.circle(frame, center, 5, (0, 0, 255), -1)
					print("{} X: {} Y: {}".format(i, x, y))
	return mask, frame

i = 1
while True:
	# ret, frame = cap.read()

	# if frame is None:
	# 	break

	mask, frame = findBall(cv2.imread('/home/bertone/Documents/Coding/PiCam-FRC-1860-2020/ball-tracking/ballImages/ball'+str(i)+'.jpeg'))

	cv2.imshow("Mask", mask)
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	if key == ord("q"):
		i+=1

# close all windows
cv2.destroyAllWindows()