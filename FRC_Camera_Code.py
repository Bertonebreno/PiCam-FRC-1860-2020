from cscore import CameraServer, UsbCamera
from networktables import NetworkTables, NetworkTablesInstance
import cv2
import numpy as np
import json
import time
from math import tan
import os

targetCameraAddress = "video0"
ballCameraAddress = "video2"

netTable = NetworkTablesInstance.getDefault()
netTable.startClientTeam(1860)

# Initializing network tables variables
netTableCalibration = netTable.getEntry("/Calibration")

netTableTargetXPos = netTable.getEntry("/Target/XPos")
netTableTargetYPos = netTable.getEntry("/Target/YPos")
netTableTargetHorizontalAngle = netTable.getEntry("/Target/HorizontalAngle")
netTableTargetLauncherAngle = netTable.getEntry("/Target/LauncherAngle")
netTableTargetDistance = netTable.getEntry("/Target/Distance")

netTableTargetHue = netTable.getEntry("/Target/Hue")
netTableTargetSaturation = netTable.getEntry("/Target/Saturation")
netTableTargetValue = netTable.getEntry("/Target/Value")

netTableTargetFocalLength = netTable.getEntry("/Target/FocalLength")
netTableTargetBrightness = netTable.getEntry("/Target/Brightness")
netTableTargetExposure = netTable.getEntry("/Target/Exposure")

netTableDistanceParameters = netTable.getEntry("/Target/DistanceParameters")



netTableBallXPos = netTable.getEntry("/Ball/XPos")
netTableBallYPos = netTable.getEntry("/Ball/YPos")
netTableBallAngle = netTable.getEntry("/Ball/Angle")

netTableBallHue = netTable.getEntry("/Ball/Hue")
netTableBallSaturation = netTable.getEntry("/Ball/Saturation")
netTableBallValue = netTable.getEntry("/Ball/Value")

netTableBallFocalLength = netTable.getEntry("/Ball/FocalLength")
netTableBallBrightness = netTable.getEntry("/Ball/Brightness")
netTableBallExposure = netTable.getEntry("/Ball/Exposure")


calibration = netTableCalibration.getBoolean(1)

focalLengthTarget = netTableTargetFocalLength.getDouble(380.191176*2)
brightnessTarget = netTableTargetBrightness.getDouble(5)
exposureTarget = netTableTargetExposure.getDouble(8)

focalLengthBall = netTableTargetFocalLength.getDouble(380.191176*2)
brightnessBall = netTableBallBrightness.getDouble(50)
exposureBall = netTableBallExposure.getDouble(50)

targetHue = netTableTargetHue.getDoubleArray([0, 0])
targetSaturation = netTableTargetSaturation.getDoubleArray([0, 0])
targetValue = netTableTargetValue.getDoubleArray([0, 0])

ballHue = netTableBallHue.getDoubleArray([0, 0])
ballSaturation = netTableBallSaturation.getDoubleArray([0, 0])
ballValue = netTableBallValue.getDoubleArray([0, 0])

distanceParameters = netTableDistanceParameters.getDoubleArray([0,0,0])

imageResolutionRasp = [1280, 720]
imageResolutionSend = [320, 180]

def getHSVTargetParameters():
    global targetHue, targetSaturation, targetValue
    # First we will try to get hsv parameters from networktables
    targetHue = netTableTargetHue.getDoubleArray([0, 0])
    targetSaturation = netTableTargetSaturation.getDoubleArray([0, 0])
    targetValue = netTableTargetValue.getDoubleArray([0, 0])
    if targetHue == [0, 0] and targetSaturation == [0, 0] and targetValue == [0, 0]:
        # Probably we are not using values from networktables, so let's take them from the internal json
        with open('parameters/hsvTarget.json', 'r') as f:
            parameters_dict = json.load(f)
        targetHue = parameters_dict['hue']
        targetSaturation = parameters_dict['sat']
        targetValue = parameters_dict['val']

def getHSVBallParameters():
    global ballHue, ballSaturation, ballValue
    # First we will try to get hsv parameters from networktables
    ballHue = netTableBallHue.getDoubleArray([0, 0])
    ballSaturation = netTableBallSaturation.getDoubleArray([0, 0])
    ballValue = netTableBallValue.getDoubleArray([0, 0])
    if ballHue == [0, 0] and ballSaturation == [0, 0] and ballValue == [0, 0]:
        # Probably we are not using values from networktables, so let's take them from the internal json
        with open('parameters/hsvBall.json', 'r') as f:
            parameters_dict = json.load(f)
        ballHue = parameters_dict['hue']
        ballSaturation = parameters_dict['sat']
        ballValue = parameters_dict['val']

def getCameraTargetParameters():
    global focalLengthTarget, brightnessTarget, exposureTarget
    # First we will try to get hsv parameters from networktables
    focalLengthTarget = netTableTargetFocalLength.getDouble(0)
    brightnessTarget = netTableTargetBrightness.getDouble(0)
    exposureTarget = netTableTargetExposure.getDouble(0)
    if focalLengthTarget == 0 and brightnessTarget == 0 and exposureTarget == 0:
        # Probably we are not using values from networktables, so let's take them from the internal json
        with open('parameters/cameraTarget.json', 'r') as f:
            parameters_dict = json.load(f)
        focalLengthTarget = parameters_dict['focalLength']
        brightnessTarget = parameters_dict['brightness']
        exposureTarget = parameters_dict['exposure']

def getCameraBallParameters():
    global focalLengthBall, brightnessBall, exposureBall
    # First we will try to get hsv parameters from networktables
    focalLengthBall = netTableBallFocalLength.getDouble(0)
    brightnessBall = netTableBallBrightness.getDouble(0)
    exposureBall = netTableBallExposure.getDouble(0)
    if focalLengthBall == 0 and brightnessBall == 0 and exposureBall == 0:
        # Probably we are not using values from networktables, so let's take them from the internal json
        with open('parameters/cameraBall.json', 'r') as f:
            parameters_dict = json.load(f)
        focalLengthBall = parameters_dict['focalLength']
        brightnessBall = parameters_dict['brightness']
        exposureBall = parameters_dict['exposure']

def getTargetDistanceParameters():
    global distanceParameters
    # First we will try to get hsv parameters from networktables
    distanceParameters = netTableDistanceParameters.getDoubleArray([0,0,0])
    if distanceParameters == [0, 0, 0]:
        # Probably we are not using values from networktables, so let's take them from the internal json
        with open('parameters/distance.json', 'r') as f:
            parameters_dict = json.load(f)
        distanceParameters[0] = parameters_dict['A']
        distanceParameters[1] = parameters_dict['B']
        distanceParameters[2] = parameters_dict['C']

getHSVBallParameters()
getHSVTargetParameters()

getCameraTargetParameters()
getCameraBallParameters()

getTargetDistanceParameters()

def calculateDistance(x):
    global distanceParameters
    a = distanceParameters[0]
    b = distanceParameters[1]
    c = distanceParameters[2]
    return a/tan(b*x + c)

def calculateCenter(contour):

    Xs, Ys = np.split(contour, 2, axis=2)
    bottom = np.amax(Ys)
    top = np.amin(Ys)
    left = np.amin(Xs)
    right = np.amax(Xs)

    centerX = int((left+right)/2)
    centerY = int((top+bottom)/2)

    return centerX, centerY

def filterContours(contours, min_area, min_perimeter,
    min_width, max_width, min_height, max_height,
    solidity, max_vertex_count, min_vertex_count,
    min_ratio, max_ratio):

    output_contours = []

    for contour in contours:

        x,y,w,h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        hull = cv2.convexHull(contour)
        solid = 100000000
        try:
            solid = 100 * area / cv2.contourArea(hull)
        except:
            pass
        ratio = (float)(w) / h

        if (w < min_width or w > max_width):
            continue
        if (h < min_height or h > max_height):
            continue
        if (area < min_area):
            continue
        if (cv2.arcLength(contour, True) < min_perimeter):
            continue
        if (solid < solidity[0] or solid > solidity[1]):
            continue
        if (len(contour) < min_vertex_count or len(contour) > max_vertex_count):
            continue
        if (ratio < min_ratio or ratio > max_ratio):
            continue

        output_contours.append(contour)

    return output_contours

def findTarget(image):
    global targetHue, targetSaturation, targetValue
    hue = targetHue
    sat = targetSaturation
    val = targetValue
    output_image = image.copy()

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    binary_image = cv2.inRange(hsv_image, (hue[0], sat[0], val[0]), (hue[1], sat[1], val[1]))
    
    _, contours, hierarchy = cv2.findContours(binary_image, mode = cv2.RETR_LIST, method = cv2.CHAIN_APPROX_SIMPLE)

    min_area = 700
    min_perimeter = 0
    min_width = 80
    max_width = 750
    min_height = 50
    max_height = 400
    solidity = [0.0, 100.0]
    max_vertex_count = 10500
    min_vertex_count = 0
    min_ratio = 0
    max_ratio = 1000

    output_contours = filterContours(contours, min_area, min_perimeter,
    min_width, max_width, min_height, max_height,
    solidity, max_vertex_count, min_vertex_count,
    min_ratio, max_ratio)
    
    cX, cY = 0, 0
    for c in output_contours:
        cX, cY = calculateCenter(c)
        cv2.circle(output_image, (cX, cY), 7, (0, 0, 255), 5)
        cv2.putText(output_image, str(cX), (cX - 20, cY - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 2)
        cv2.putText(output_image, str(cY), (cX + 20, cY - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 2)
    
    centerX, centerY = 0, 0

    if len(output_contours) > 0:
        centerX, centerY = calculateCenter(output_contours[0])
    
    return output_image, binary_image, centerX, centerY

def findBall(image):
    hue = ballHue
    sat = ballSaturation
    val = ballValue
    output_image = image.copy()

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    binary_image = cv2.inRange(hsv_image, (hue[0], sat[0], val[0]), (hue[1], sat[1], val[1]))
    
    _, contours, hierarchy = cv2.findContours(binary_image, mode = cv2.RETR_LIST, method = cv2.CHAIN_APPROX_SIMPLE)

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

    output_contours = filterContours(contours, min_area, min_perimeter,
    min_width, max_width, min_height, max_height,
    solidity, max_vertex_count, min_vertex_count,
    min_ratio, max_ratio)
    
    biggerX, biggerY = 0, 0
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

    return output_image, binary_image, biggerX, biggerY

def getHorizontalAngle(x, imageResolution):
    global focalLengthTarget
    angle = np.arctan((x - (imageResolution[0]-1)/2)/focalLengthTarget)*180/np.pi
    return angle

def getLauncherAngle(x):
    return 3/22*x - 135/11

def main():

    cs = CameraServer.getInstance()
    cs.enableLogging()
    outputStreamTarget = cs.putVideo("targetImage", imageResolutionSend[0], imageResolutionSend[1])
    outputStreamTargetBinary = cs.putVideo("targetImageBinary", imageResolutionSend[0], imageResolutionSend[1])
    outputStreamBall = cs.putVideo("ballImage", imageResolutionSend[0], imageResolutionSend[1])
    outputStreamBallBinary = cs.putVideo("ballImageBinary", imageResolutionSend[0], imageResolutionSend[1])

    targetImage = np.zeros(shape=(imageResolutionRasp[1], imageResolutionRasp[0], 3), dtype=np.uint8)
    ballImage = np.zeros(shape=(imageResolutionRasp[1], imageResolutionRasp[0], 3), dtype=np.uint8)

    availableTargetCamera = targetCameraAddress in os.listdir("/dev")
    availableBallCamera = ballCameraAddress in os.listdir("/dev")

    if availableTargetCamera:
        cameraTarget = UsbCamera("Camera Target", "/dev/" + targetCameraAddress)
        cameraTarget.setResolution(imageResolutionRasp[0], imageResolutionRasp[1])
        cameraTarget.setBrightness(brightnessTarget)
        cameraTarget.setExposureManual(exposureTarget)
        cs.addCamera(cameraTarget)
        cvSinkTarget = cs.getVideo(name="Camera Target")
        cvSinkTarget.setSource(cameraTarget)

    if availableBallCamera:
        cameraBall = UsbCamera("Camera Ball", "/dev/" + ballCameraAddress)
        cameraBall.setResolution(imageResolutionRasp[0], imageResolutionRasp[1])
        cameraBall.setBrightness(brightnessBall)
        cameraBall.setExposureManual(exposureBall)
        cs.addCamera(cameraBall)
        cvSinkBall = cs.getVideo(name="Camera Ball")
        cvSinkBall.setSource(cameraBall)
    
    counter = 0
    while True:

        if availableTargetCamera:
            availableTargetCamera = targetCameraAddress in os.listdir("/dev")
        if availableBallCamera:
            availableBallCamera = ballCameraAddress in os.listdir("/dev")

        counter += 1
        textOutput = ""

        if calibration:
            
            getHSVBallParameters()
            getHSVTargetParameters()
            
            getCameraTargetParameters()
            getCameraBallParameters()

            getTargetDistanceParameters()
        
        if availableTargetCamera:
            t, targetImage = cvSinkTarget.grabFrame(targetImage)
            targetImage, binaryTargetImage, targetXPos, targetYPos = findTarget(targetImage)
            distance = calculateDistance(targetYPos)
            horizontalAngle = getHorizontalAngle(targetXPos, imageResolutionRasp)
            launcherAngle = getLauncherAngle(distance)

            netTableTargetDistance.setDouble(distance)
            netTableTargetHorizontalAngle.setDouble(horizontalAngle)
            netTableTargetLauncherAngle.setDouble(launcherAngle)
            netTableTargetXPos.setDouble(targetXPos)
            netTableTargetYPos.setDouble(targetYPos)
            smallerBinaryTargetImage = cv2.resize(binaryTargetImage, (imageResolutionSend[0], imageResolutionSend[1]))
            smallerTargetImage = cv2.resize(targetImage, (imageResolutionSend[0], imageResolutionSend[1]))
            outputStreamTargetBinary.putFrame(smallerBinaryTargetImage)
            outputStreamTarget.putFrame(smallerTargetImage)
            textOutput += "Distance: {} horizontalAngle: {} launcherAngle: {} targetYPos: {}\n".format(distance, horizontalAngle, launcherAngle, targetYPos)
        else:
            textOutput += "Target Camera disabled\n"


        if availableBallCamera:
            t, ballImage = cvSinkBall.grabFrame(ballImage)
            ballImage, binaryBallImage, ballXPos, ballYPos = findBall(ballImage)
            # netTableBallXPos.setDouble(ballXPos)
            # netTableBallYPos.setDouble(ballYPos)
            smallerBinaryBallImage = cv2.resize(binaryBallImage, (imageResolutionSend[0], imageResolutionSend[1]))
            smallerBallImage = cv2.resize(ballImage, (imageResolutionSend[0], imageResolutionSend[1]))
            outputStreamBallBinary.putFrame(smallerBinaryBallImage)
            outputStreamBall.putFrame(smallerBallImage)
            # textOutput += "ballXPos: {} ballYPos: {}\n".format(ballXPos, ballYPos)
        else:
            textOutput += "Ball Camera disabled\n"

        if counter % 10 == 0:
            print(textOutput)
main()