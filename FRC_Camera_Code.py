from cscore import CameraServer, UsbCamera
from networktables import NetworkTables, NetworkTablesInstance
import ntcore
import cv2
import numpy as np
import json
import logging
import time
from math import tan

logging.basicConfig(level=logging.DEBUG)

netTable = NetworkTablesInstance.getDefault()
netTable.startClientTeam(1860)

netTableCalibration = netTable.getEntry("/Calibration")
netTableDistance = netTable.getEntry("Target/Distance")
netTableXPos = netTable.getEntry("Target/XPos")
netTableYPos = netTable.getEntry("Target/YPos")
netTableAngle = netTable.getEntry("/Angle")
netTableHue = netTable.getEntry("/Camera/Hue")
netTableSaturation = netTable.getEntry("/Camera/Saturation")
netTableValue = netTable.getEntry("/Camera/Value")
netTableFocalLength = netTable.getEntry("/Camera/FocalLength")
netTableCameraBrightness = netTable.getEntry("/Camera/Brightness")
netTableCameraExposure = netTable.getEntry("/Camera/Exposure")
netTableDistanceParameters = netTable.getEntry("/Camera/DistanceParameters")

calibration = netTableCalibration.getBoolean(1)
focalLength = netTableFocalLength.getDouble(380.191176*2)
cameraHeight = netTableCameraHeight.getDouble(1)
brightness = netTableCameraBrightness.getDouble(5)
exposure = netTableCameraExposure.getDouble(8)
distanceParameters = netTableDistanceParameters.getDoubleArray([0,0,0])

total = 1
achou = 1

class GripPipeline:
    
    def __init__(self):

        self.__hsv_threshold_hue = [0.0, 180.0]
        self.__hsv_threshold_saturation = [123.83093415833206, 255.0]
        self.__hsv_threshold_value = [155.93524851816161, 249.197957751694]
        self.getHSVParameters()
        self.hsv_threshold_output = None

        self.__find_contours_input = self.hsv_threshold_output
        self.__find_contours_external_only = False

        self.find_contours_output = None

        self.__filter_contours_contours = self.find_contours_output
        self.__filter_contours_min_area = 700
        self.__filter_contours_min_perimeter = 0.0
        self.__filter_contours_min_width = 80.0
        self.__filter_contours_max_width = 750.0
        self.__filter_contours_min_height = 50.0
        self.__filter_contours_max_height = 400.0
        self.__filter_contours_solidity = [0.0, 100.0]
        self.__filter_contours_max_vertices = 10500.0
        self.__filter_contours_min_vertices = 0.0
        self.__filter_contours_min_ratio = 0.0
        self.__filter_contours_max_ratio = 1000.0

        self.filter_contours_output = None

    def getHSVParameters(self):
        try:
            # First we will try to get hsv parameters from networktables
            self.__hsv_threshold_hue = netTableHue.getDoubleArray([0, 0])
            self.__hsv_threshold_saturation = netTableSaturation.getDoubleArray([0, 0])
            self.__hsv_threshold_value = netTableValue.getDoubleArray([0, 0])
            if self.__hsv_threshold_hue == [0, 0] and self.__hsv_threshold_saturation == [0, 0] and self.__hsv_threshold_value == [0, 0]:
                # Probably we are not using values from networktables, so let's take them from the internal json
                with open('parameters.json', 'r') as f:
                    parameters_dict = json.load(f)
                self.__hsv_threshold_hue = parameters_dict['hue']
                self.__hsv_threshold_saturation = parameters_dict['sat']
                self.__hsv_threshold_value = parameters_dict['val']
        except:
            print("Error HSV parameters")


    def process(self, source0):

        # Step HSV_Threshold0:
        self.__hsv_threshold_input = source0
        (self.hsv_threshold_output) = self.__hsv_threshold(self.__hsv_threshold_input, self.__hsv_threshold_hue, self.__hsv_threshold_saturation, self.__hsv_threshold_value)
        # Step Find_Contours0:
        self.__find_contours_input = self.hsv_threshold_output
        (self.find_contours_output) = self.__find_contours(self.__find_contours_input, self.__find_contours_external_only)
        

        # Step Filter_Contours0:
        self.__filter_contours_contours = self.find_contours_output
        (self.filter_contours_output) = self.__filter_contours(self.__filter_contours_contours, self.__filter_contours_min_area, self.__filter_contours_min_perimeter, self.__filter_contours_min_width, self.__filter_contours_max_width, self.__filter_contours_min_height, self.__filter_contours_max_height, self.__filter_contours_solidity, self.__filter_contours_max_vertices, self.__filter_contours_min_vertices, self.__filter_contours_min_ratio, self.__filter_contours_max_ratio)
        
        baseImage = source0
        cv2.drawContours(baseImage, self.filter_contours_output, -1, (0,255,0), 3)
        #obtain the first 2 points of contours
        cntx1 = self.filter_contours_output
        cntx = self.filter_contours_output
        global total
        global achou
        total += 1
        try:
            c = cntx[0]
            extLeft = tuple(c[c[:, :, 0].argmin()][0])
            cv2.circle(baseImage, extLeft, 7, (0, 0, 255), 5)
            extRight = tuple(c[c[:, :, 0].argmax()][0])
            cv2.circle(baseImage, extRight, 7, (0, 0, 255), 5)
            extTop = tuple(c[c[:, :, 1].argmin()][0])
            cv2.circle(baseImage, extTop, 7, (0, 0, 255), 5)
            extBottom = tuple(c[c[:, :, 1].argmax()][0]) 
            cv2.circle(baseImage, extBottom, 7, (0, 0, 255), 5)
            achou += 1
            centerX = int((extLeft[0]+extRight[0])/2)
            centerY = int((extTop[1]+extBottom[1])/2)
            cv2.circle(baseImage, (centerX, centerY), 7, (255, 0, 255), 5)
            #print("left:{} right:{} top:{} bottom:{}".format(extLeft, extRight, extTop, extBottom))
        except:
            pass
            #print("nao tem")
        cX, cY = 0, 0
        for c in self.filter_contours_output:
            # compute the center of the contour
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(baseImage, (cX, cY), 7, (0, 0, 255), 5)
            cv2.drawContours(baseImage, self.filter_contours_output, -1, (0,255,0), 3)
            cv2.putText(baseImage, str(cX), (cX - 20, cY - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 2)
            cv2.putText(baseImage, str(cY), (cX + 20, cY - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 2)
            #cv2.rectangle(baseImage, (500, 300), (700,500), (255, 0, 0), 10)
        return baseImage, self.hsv_threshold_output, centerX, centerY

    @staticmethod
    def __hsv_threshold(input, hue, sat, val):

        out = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
        return cv2.inRange(out, (hue[0], sat[0], val[0]),  (hue[1], sat[1], val[1]))

    @staticmethod
    def __find_contours(input, external_only):

        if(external_only):
            mode = cv2.RETR_EXTERNAL
        else:
            mode = cv2.RETR_LIST
        method = cv2.CHAIN_APPROX_SIMPLE
        im2, contours, hierarchy = cv2.findContours(input, mode = mode, method = method)
        return contours

    @staticmethod
    def __filter_contours(input_contours, min_area, min_perimeter, min_width, max_width,
                        min_height, max_height, solidity, max_vertex_count, min_vertex_count,
                        min_ratio, max_ratio):

        output = []
        for contour in input_contours:
            x,y,w,h = cv2.boundingRect(contour)
            if (w < min_width or w > max_width):
                continue
            if (h < min_height or h > max_height):
                continue
            area = cv2.contourArea(contour)
            if (area < min_area):
                continue
            if (cv2.arcLength(contour, True) < min_perimeter):
                continue
            hull = cv2.convexHull(contour)
            solid = 100 * area / cv2.contourArea(hull)
            if (solid < solidity[0] or solid > solidity[1]):
                continue
            if (len(contour) < min_vertex_count or len(contour) > max_vertex_count):
                continue
            ratio = (float)(w) / h
            if (ratio < min_ratio or ratio > max_ratio):
                continue
            output.append(contour)
        return output


def expo(number, times):
    x = 1
    for i in range(times):
        x*=number
    return x

def findDistance(imageHeight, parameters=[62.699739242018275 ,-0.0006735027970270629,  0.564385170675513]):
    return parameters[0]/tan(parameters[1]*imageHeight+parameters[2])

def getBallColorParameters():
    hue = [0,255]
    sat = [0,255]
    val = [0,255]
    try:
        with open('ballColorParameters.json', 'r') as f:
            parameters_dict = json.load(f)
        hue = parameters_dict['hue']
        sat = parameters_dict['sat']
        val = parameters_dict['val']
    except:
        print("Error ball color parameters")
    return hue, sat, val

def findBall(imageFrame):
    blurred = cv2.GaussianBlur(imageFrame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    hue, sat, val = getBallColorParameters()
    mask = cv2.inRange(hsv, (hue[0], sat[0], val[0]),  (hue[1], sat[1], val[1]))
    mask = cv2.erode(mask, None, iterations=4)
    mask = cv2.dilate(mask, None, iterations=4)
    #cv2.imshow("Binary", mask)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    if len(cnts) > 0:
        for i in range(len(cnts)):
            approx = cv2.approxPolyDP(cnts[i],0.01*cv2.arcLength(cnts[i],True),True)
            contourArea = cv2.contourArea(cnts[i])
            print("CA: ",contourArea)
            cv2.drawContours(imageFrame, cnts[i], -1, (0,255,0), 3)
            ((x, y), radius) = cv2.minEnclosingCircle(cnts[i])
            minEnclosingCircleArea = np.pi*radius**2
            print("MIN: ", minEnclosingCircleArea)
            areaRatio = contourArea/(minEnclosingCircleArea)
            if 0.7<areaRatio and areaRatio<1.3:
                if radius>15:
                    M = cv2.moments(cnts[i])
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    cv2.circle(imageFrame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(imageFrame, center, 5, (0, 0, 255), -1)
                    print("{} X: {} Y: {}".format(i, x, y))
    return imageFrame

#Returns an array [XAngle, YAngle] 
def getAngle(position, imageResolution): 
    XAngle = np.arctan((position[0] - (imageResolution[0]-1)/2)/focalLength)*180/np.pi
    YAngle = np.arctan((position[1] - (imageResolution[1]-1)/2)/focalLength)*180/np.pi
    angle = [XAngle, YAngle]
    return angle

def getCameraParameters():
    try:
        focalLength = netTableFocalLength.getDouble(380.191176*2)
        brightness = netTableCameraBrightness.getDouble(5)
        exposure = netTableCameraExposure.getDouble(8)
    except:
        print("Error Camera parameters")

def getDistanceParameters():
    parameters = [0,0,0]
    try:
        with open('distanceParameters.json', 'r') as f:
            parameters_dict = json.load(f)
        parameters[0] = parameters_dict['A']
        parameters[1] = parameters_dict['B']
        parameters[2] = parameters_dict['C']
    except:
        print("Error distance parameters")
    return parameters


processImage = GripPipeline()
def main():
    imageResolutionRasp = [1280, 720]
    imageResolutionSend = [320, 180]

    cs = CameraServer.getInstance()
    cs.enableLogging()
    outputStreamEdited = cs.putVideo("processedImage", imageResolutionSend[0], imageResolutionSend[1])
    outputStreamBinary = cs.putVideo("binaryImage", imageResolutionSend[0], imageResolutionSend[1])
    img = np.zeros(shape=(imageResolutionRasp[1], imageResolutionRasp[0], 3), dtype=np.uint8)

    camera = UsbCamera("Camera", "/dev/video0")
    camera.setResolution(imageResolutionRasp[0], imageResolutionRasp[1])
    camera.setBrightness(brightness)
    camera.setExposureManual(exposure)
    cs.addCamera(camera)
    cvSink = cs.getVideo()
    cvSink.setSource(camera)
    tempoInicial = time.time()
    timePassed = 0
    while True:
        if(calibration):
            processImage.getHSVParameters()
            getCameraParameters()
        t, img = cvSink.grabFrame(img)
        processedImage, binaryImage, objectXPos, objectYPos = processImage.process(img)

        distance = findDistance(objectYPos, getDistanceParameters())
        angle = getAngle([objectXPos, objectYPos], imageResolutionRasp)

        netTableDistance.setDouble(distance)
        netTableAngle.setDoubleArray(angle)

        timeDifference = time.time() - tempoInicial
        if timeDifference > 2:
            print("Time: {} Distance: {} XPos: {} YPos: {}".format(timePassed, distance, objectXPos, objectYPos))
            print("qualidade do filtro HSV: ", achou/total*100, "%")
            tempoInicial = time.time()
            timePassed+=2

        smallerProcessedImage = cv2.resize(processedImage, (imageResolutionSend[0], imageResolutionSend[1]))
        smallerBinaryImage = cv2.resize(binaryImage, (imageResolutionSend[0], imageResolutionSend[1]))
        outputStreamEdited.putFrame(smallerProcessedImage)
        outputStreamBinary.putFrame(smallerBinaryImage)
        #outputStreamBall.putFrame(ballImage)
main()