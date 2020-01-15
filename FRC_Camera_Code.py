from cscore import CameraServer
from networktables import NetworkTables, NetworkTablesInstance
import ntcore
import cv2
import numpy as np
import json
import logging

logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize(server='roborio-1860-frc.local')
netTable = NetworkTablesInstance.getDefault()
netTable.startClientTeam(1860)

netTableCalibracao = netTable.getEntry("/CALIBRACAO")
CALIBRACAO = netTableCalibracao.getBoolean(0)

netTableHue = netTable.getEntry("/Camera/Hue")
netTableSaturation = netTable.getEntry("/Camera/Saturation")
netTableValue = netTable.getEntry("/Camera/Value")
netTableFocalLength = netTable.getEntry("/Camera/FocalLength")
netTableCameraHeight = netTable.getEntry("/Camera/Height")

netTableHue.forceSetDoubleArray([0.0, 180.0])
netTableSaturation.forceSetDoubleArray([123.83093415833206, 255.0])
netTableValue.forceSetDoubleArray([155.93524851816161, 249.197957751694])

class GripPipeline:
    """
    An OpenCV pipeline generated by GRIP.
    """
    
    def init(self):
        """initializes all values to presets or None if need to be set
        """
        """initializes all values to presets or None if need to be set
        """
        self.hsv_threshold_hue = [0.0, 180.0]
        self.hsv_threshold_saturation = [123.83093415833206, 255.0]
        self.hsv_threshold_value = [155.93524851816161, 249.197957751694]
        self.getHSVParameters()
        self.hsv_threshold_output = None

        self.find_contours_input = self.hsv_threshold_output
        self.find_contours_external_only = False

        self.find_contours_output = None

        self.filter_contours_contours = self.find_contours_output
        self.filter_contours_min_area = 500.0
        self.filter_contours_min_perimeter = 0.0
        self.filter_contours_min_width = 0.0
        self.filter_contours_max_width = 1000.0
        self.filter_contours_min_height = 0.0
        self.filter_contours_max_height = 1000.0
        self.filter_contours_solidity = [0.0, 100.0]
        self.filter_contours_max_vertices = 1000000.0
        self.filter_contours_min_vertices = 0.0
        self.filter_contours_min_ratio = 0.0
        self.filter_contours_max_ratio = 1000.0

        self.filter_contours_output = None

    def getHSVParameters(self):
        try:
            self.hsv_threshold_hue = netTableHue.getDoubleArray(0)
            self.hsv_threshold_saturation = netTableSaturation.getDoubleArray(0)
            self.hsv_threshold_value = netTableValue.getDoubleArray(0)

        except:
            print("Error HSV parameters")

    def getCameraParameters(self):
        try:
            self.focalLength = netTableFocalLength.getDouble(1)
            self.cameraHeight = netTableCameraHeight.getDouble(1)

        except:
            print("Error Camera parameters")

    def process(self, source0):
        """
        Runs the pipeline and sets all outputs to new values.
        """
        # Step HSV_Threshold0:
        self.hsv_threshold_input = source0
        (self.hsv_threshold_output) = self.hsv_threshold(self.hsv_threshold_input, self.hsv_threshold_hue, self.hsv_threshold_saturation, self.hsv_threshold_value)
        # Step Find_Contours0:
        self.find_contours_input = self.hsv_threshold_output
        (self.find_contours_output) = self.find_contours(self.find_contours_input, self.find_contours_external_only)
        

        # Step Filter_Contours0:
        self.filter_contours_contours = self.find_contours_output
        (self.filter_contours_output) = self.filter_contours(self.filter_contours_contours, self.filter_contours_min_area, self.filter_contours_min_perimeter, self.filter_contours_min_width, self.filter_contours_max_width, self.filter_contours_min_height, self.filter_contours_max_height, self.filter_contours_solidity, self.filter_contours_max_vertices, self.filter_contours_min_vertices, self.filter_contours_min_ratio, self.filter_contours_max_ratio)
        
        imagem_teste = source0
        cv2.drawContours(imagem_teste, self.filter_contours_output, -1, (0,255,0), 3)
        
        #obtain the first 2 points of contours
        cntx1 = self.filter_contours_output
        cntx = self.filter_contours_output
        cX, cY = 0, 0
        for c in self.filter_contours_output:
            # compute the center of the contour
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(source0, (cX, cY), 7, (0, 0, 255), 5)
            cv2.drawContours(source0, self.filter_contours_output, -1, (0,255,0), 3)
            cv2.putText(source0, str(cX), (cX - 20, cY - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(source0, str(cY), (cX - 40, cY - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        return imagem_teste, self.hsv_threshold_output, cX, cY

    @staticmethod
    def hsv_threshold(input, hue, sat, val):
        """Segment an image based on hue, saturation, and value ranges.
        Args:
            input: A BGR numpy.ndarray.
            hue: A list of two numbers the are the min and max hue.
            sat: A list of two numbers the are the min and max saturation.
            lum: A list of two numbers the are the min and max value.
        Returns:
            A black and white numpy.ndarray.
        """
        out = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
        return cv2.inRange(out, (hue[0], sat[0], val[0]),  (hue[1], sat[1], val[1]))

    @staticmethod
    def find_contours(input, external_only):
        """Sets the values of pixels in a binary image to their distance to the nearest black pixel.
        Args:
            input: A numpy.ndarray.
            external_only: A boolean. If true only external contours are found.
        Return:
            A list of numpy.ndarray where each one represents a contour.
        """
        if(external_only):
            mode = cv2.RETR_EXTERNAL
        else:
            mode = cv2.RETR_LIST
        method = cv2.CHAIN_APPROX_SIMPLE
        im2, contours, hierarchy =cv2.findContours(input, mode=mode, method = method)
        return contours

    @staticmethod
    def filter_contours(input_contours, min_area, min_perimeter, min_width, max_width,
                        min_height, max_height, solidity, max_vertex_count, min_vertex_count,
                        min_ratio, max_ratio):
        """Filters out contours that do not meet certain criteria.
        Args:
            input_contours: Contours as a list of numpy.ndarray.
            min_area: The minimum area of a contour that will be kept.
            min_perimeter: The minimum perimeter of a contour that will be kept.
            min_width: Minimum width of a contour.
            max_width: MaxWidth maximum width.
            min_height: Minimum height.
            max_height: Maximimum height.
            solidity: The minimum and maximum solidity of a contour.
            min_vertex_count: Minimum vertex Count of the contours.
            max_vertex_count: Maximum vertex Count.
            min_ratio: Minimum ratio of width to height.
            max_ratio: Maximum ratio of width to height.
        Returns:
            Contours as a list of numpy.ndarray.
        """
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

def findDistance(imageHeight, parameters):
    return parameters[0]/np.tan(parameters[1]*imageHeight+parameters[2])

#Returns an array [XAngle, YAngle] 
def getAngleDif(position, imageResolution): 
    XAngle = np.arctan((position[0] - (imageResolution[0]-1)/2)/processImage.focalLength)
    YAngle = np.arctan((position[1] - (imageResolution[1]-1)/2)/processImage.focalLength) 
    angle = [XAngle, YAngle]
    return angle

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
    distanceParameters = getDistanceParameters()
    imageResolution = [320, 240]

    cs = CameraServer.getInstance()
    cs.enableLogging()
    camera = cs.startAutomaticCapture()
    camera.setResolution(imageResolution[0], imageResolution[1])
    cvSink = cs.getVideo()
    outputStreamEdited = cs.putVideo("processedImage", imageResolution[0], imageResolution[1])
    outputStreamBinary = cs.putVideo("binaryImage", imageResolution[0], imageResolution[1])
    img = np.zeros(shape=(imageResolution[1], imageResolution[0], 3), dtype=np.uint8) #240 lines and 320 columns

    while True:
        if(CALIBRACAO == True):
            processImage.getHSVParameters()
            processImage.getCameraParameters()
        t, img = cvSink.grabFrame(img)
        if t == 0:
            outputStreamEdited.notifyError(cvSink.getError());
            continue
        processedImage, binaryImage, objectXPos, objectYPos = processImage.process(img)
        netTableDistance = netTable.getEntry("/Distance")
        distance = findDistance(objectYPos, distanceParameters)
        print(getAngleDif([objectXPos, objectYPos], imageResolution))
        outputStreamEdited.putFrame(processedImage)
        outputStreamBinary.putFrame(binaryImage)
main()
