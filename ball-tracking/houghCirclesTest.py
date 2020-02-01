import cv2
import numpy as np

img = cv2.imread('/home/bertone/Downloads/WhatsApp Image 2020-01-31 at 19.13.17 (3).jpeg',0)
img = cv2.resize(img, (240, 320))
img = cv2.medianBlur(img,5)
#cimg = cv2.cvtColor(img,cv2.COLOR_BGR2BGR)

circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT, 30, 170,
                            param1=50,param2=100,minRadius=25,maxRadius=90)

circles = np.uint16(np.around(circles))
for i in circles[0,:]:
    # draw the outer circle
    cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
    # draw the center of the circle
    cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)

print(img.shape)
cv2.imshow('detected circles', img)
cv2.waitKey(0)
cv2.destroyAllWindows()