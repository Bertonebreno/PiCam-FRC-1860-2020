from cscore import CameraServer, UsbCamera
from networktables import NetworkTables, NetworkTablesInstance
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
netTableDistance = netTable.getEntry("/Target/Distance")
netTableAngle = netTable.getEntry("/Target/Angle")

netTableTargetXPos = netTable.getEntry("/Target/XPos")
netTableTargetYPos = netTable.getEntry("/Target/YPos")

netTableBallXPos = netTable.getEntry("/Ball/XPos")
netTableBallYPos = netTable.getEntry("/Ball/YPos")

netTableTargetHue = netTable.getEntry("/CameraTarget/Hue")
netTableTargetSaturation = netTable.getEntry("/CameraTarget/Saturation")
netTableTargetValue = netTable.getEntry("/CameraTarget/Value")

netTableBallHue = netTable.getEntry("/CameraBall/Hue")
netTableBallSaturation = netTable.getEntry("/CameraBall/Saturation")
netTableBallValue = netTable.getEntry("/CameraBall/Value")

netTableTargetFocalLength = netTable.getEntry("/CameraTarget/FocalLength")
netTableTargetBrightness = netTable.getEntry("/CameraTarget/Brightness")
netTableTargetExposure = netTable.getEntry("/CameraTarget/Exposure")

netTableBallBrightness = netTable.getEntry("/CameraBall/Brightness")
netTableBallExposure = netTable.getEntry("/CameraBall/Exposure")

netTableDistanceParameters = netTable.getEntry("/CameraTarget/DistanceParameters")


calibration = netTableCalibration.getBoolean(1)

focalLengthTarget = netTableTargetFocalLength.getDouble(380.191176*2)
brightnessTarget = netTableTargetBrightness.getDouble(5)
exposureTarget = netTableTargetExposure.getDouble(8)

brightnessBall = netTableBallBrightness.getDouble(50)
exposureBall = netTableBallExposure.getDouble(50)

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
            self.__hsv_threshold_hue = netTableTargetHue.getDoubleArray([0, 0])
            self.__hsv_threshold_saturation = netTableTargetSaturation.getDoubleArray([0, 0])
            self.__hsv_threshold_value = netTableTargetValue.getDoubleArray([0, 0])
            if self.__hsv_threshold_hue == [0, 0] and self.__hsv_threshold_saturation == [0, 0] and self.__hsv_threshold_value == [0, 0]:
                # Probably we are not using values from networktables, so let's take them from the internal json
                with open('targetParameters.json', 'r') as f:
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
        centerX, centerY = 0, 0
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
        contours, hierarchy = cv2.findContours(input, mode = mode, method = method)
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

def findDistance(x, parameters = [62.699739242018275 ,-0.0006735027970270629,  0.564385170675513]):
    return parameters[0]/tan(parameters[1]*x + parameters[2])

def getBallParameters():
    hue = [0,255]
    sat = [0,255]
    val = [0,255]
    try:
        with open('ballParameters.json', 'r') as f:
            parameters_dict = json.load(f)
        hue = parameters_dict['hue']
        sat = parameters_dict['sat']
        val = parameters_dict['val']
    except:
        print("Error ball parameters")
    return [hue, sat, val]

def findBalls(image, hsvParameters):
    hue = hsvParameters[0]
    sat = hsvParameters[1]
    val = hsvParameters[2]
    output_image = image.copy()
    binary_image = cv2.inRange(image, (hue[0], sat[0], val[0]), (hue[1], sat[1], val[1]))
    contours, hierarchy = cv2.findContours(binary_image, mode = cv2.RETR_LIST, method = cv2.CHAIN_APPROX_SIMPLE)

    min_area = 100
    min_perimeter = 0
    min_width = 0
    max_width = 750
    min_height = 0
    max_height = 400
    solidity = [0.0, 100.0]
    max_vertex_count = 10500
    min_vertex_count = 0
    min_ratio = 0
    max_ratio = 1000

    output_contours = []
    for contour in contours:
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
        output_contours.append(contour)
    
    biggerX, biggerY = 0, 0
    try:
        cX, cY = 0, 0
        biggerCont = []
        biggerSize = 0
        biggerId = 0
        for i in range(len(output_contours)):
            c = output_contours[i]
            Xs, Ys = np.split(c, 2, axis=2)
            bottom = np.amax(Ys)
            top = np.amin(Ys)
            left = np.amin(Xs)
            right = np.amax(Xs)
            if max(bottom-top, right-left) > biggerSize:
                biggerSize = max(top-bottom, right-left)
                biggerCont = c.copy()
                biggerId = i
        for i in range(len(output_contours)):
            c = output_contours[i]
            Xs, Ys = np.split(c, 2, axis=2)
            bottom = np.amax(Ys)
            top = np.amin(Ys)
            left = np.amin(Xs)
            right = np.amax(Xs)
            M = cv2.moments(c)
            cX = int((right + left)/2)
            cY = int((top + bottom)/2)
            radius = int(max(top-bottom, right-left)/2)
            cv2.circle(output_image, (cX, cY), 7, (0, 0, 255), 5)
            cv2.putText(output_image, str(cX), (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 2)
            cv2.putText(output_image, str(cY), (cX + 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 2)
            if i == biggerId:
                biggerX, biggerY = cX, cY
                cv2.circle(output_image, (cX, cY), radius, (0, 255, 0), 3)
            else:
                cv2.circle(output_image, (cX, cY), radius, (255, 0, 0), 3)
    except:
        print("deu ruim")

    return output_image, binary_image, biggerX, biggerY

#Returns an array [XAngle, YAngle] 
def getAngle(position, imageResolution): 
    XAngle = np.arctan((position[0] - (imageResolution[0]-1)/2)/focalLengthTarget)*180/np.pi
    YAngle = np.arctan((position[1] - (imageResolution[1]-1)/2)/focalLengthTarget)*180/np.pi
    angle = [XAngle, YAngle]
    return angle

def getCameraParameters():
    try:
        focalLengthTarget = netTableTargetFocalLength.getDouble(380.191176*2)
        brightnessTarget = netTableTargetBrightness.getDouble(5)
        exposureTarget = netTableTargetExposure.getDouble(8)
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
    outputStreamTarget = cs.putVideo("targetImage", imageResolutionSend[0], imageResolutionSend[1])
    outputStreamBall = cs.putVideo("ballImage", imageResolutionSend[0], imageResolutionSend[1])
    
    targetImage = np.zeros(shape=(imageResolutionRasp[1], imageResolutionRasp[0], 3), dtype=np.uint8)
    ballImage = np.zeros(shape=(imageResolutionRasp[1], imageResolutionRasp[0], 3), dtype=np.uint8)

    cameraTarget = UsbCamera("Camera Target", "/dev/video4")
    cameraTarget.setResolution(imageResolutionRasp[0], imageResolutionRasp[1])
    cameraTarget.setBrightness(brightnessTarget)
    cameraTarget.setExposureManual(exposureTarget)
    cs.addCamera(cameraTarget)
    cvSinkTarget = cs.getVideo(name="Camera Target")
    cvSinkTarget.setSource(cameraTarget)

    cameraBall = UsbCamera("Camera Ball", "/dev/video2")
    cameraBall.setResolution(imageResolutionRasp[0], imageResolutionRasp[1])
    cameraBall.setBrightness(brightnessBall)
    cameraBall.setExposureManual(exposureBall)
    cs.addCamera(cameraBall)
    cvSinkBall = cs.getVideo(name="Camera Ball")
    cvSinkBall.setSource(cameraBall)

    tempoInicial = time.time()
    timePassed = 0
    while True:
        if(calibration):
            processImage.getHSVParameters()
            getCameraParameters()
        t, targetImage = cvSinkTarget.grabFrame(targetImage)
        t, ballImage = cvSinkBall.grabFrame(ballImage)

        targetImage, binaryTargetImage, targetXPos, targetYPos = processImage.process(targetImage)
        ballImage, binaryBallImage, ballXPos, ballYPos = findBalls(ballImage, getBallParameters())

        distance = findDistance(targetYPos, getDistanceParameters())
        angle = getAngle([targetXPos, targetYPos], imageResolutionRasp)

        netTableDistance.setDouble(distance)
        netTableAngle.setDoubleArray(angle)
        netTableBallXPos.setDouble(ballXPos)
        netTableBallYPos.setDouble(ballYPos)
        netTableTargetXPos.setDouble(targetXPos)
        netTableTargetYPos.setDouble(targetYPos)

        timeDifference = time.time() - tempoInicial
        if timeDifference > 2:
            print("Time: {} Distance: {} XPos: {} YPos: {}".format(timePassed, distance, targetXPos, targetYPos))
            print("qualidade do filtro HSV: ", achou/total*100, "%")
            tempoInicial = time.time()
            timePassed+=2
        
        smallerTargetImage = cv2.resize(targetImage, (imageResolutionSend[0], imageResolutionSend[1]))
        smallerBallImage = cv2.resize(ballImage, (imageResolutionSend[0], imageResolutionSend[1]))
        outputStreamTarget.putFrame(smallerTargetImage)
        outputStreamBall.putFrame(smallerBallImage)
        
        if cv2.waitKey(1) == 27:
            exit(0)
main()