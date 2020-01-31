from tkinter import *
from networktables import NetworkTables, NetworkTablesInstance
from math import atan
import numpy as np
from scipy.optimize import minimize, root_scalar
import logging

netTable = NetworkTablesInstance.getDefault()
netTable.startClientTeam(1860)
netTableDistance = netTable.getEntry("/Distance")
netTableXPos = netTable.getEntry("/XPos")
netTableYPos = netTable.getEntry("/YPos")
netTableAngle = netTable.getEntry("/Angle")
netTableHue = netTable.getEntry("/Camera/Hue")
netTableSaturation = netTable.getEntry("/Camera/Saturation")
netTableValue = netTable.getEntry("/Camera/Value")
netTableCameraBrightness = netTable.getEntry("/Camera/Brightness")
netTableCameraExposure = netTable.getEntry("/Camera/Exposure")
netTableDistanceParameters = netTable.getEntry("/Camera/DistanceParameters")

distanceMeasurementsValues = []
distanceMeasurementsWidgets = []

bigFont = ("Arial", 20)
mediumFont = ("Arial", 15)

window = Tk()
window.title("Master Calibrator 1860")
window.geometry('800x600')
# creating functions
def getColorParameters():

    hueRange = netTableHue.getDoubleArray([0, 255])
    satRange = netTableSaturation.getDoubleArray([0, 255])
    valRange = netTableValue.getDoubleArray([0, 255])

    hueMinSlider.set(hueRange[0])
    hueMaxSlider.set(hueRange[1])
    satMinSlider.set(satRange[0])
    satMaxSlider.set(satRange[1])
    valMinSlider.set(valRange[0])
    valMaxSlider.set(valRange[1])


def setColorParameters(a):

    hueMin = hueMinSlider.get()
    hueMax = hueMaxSlider.get()
    satMin = satMinSlider.get()
    satMax = satMaxSlider.get()
    valMin = valMinSlider.get()
    valMax = valMaxSlider.get()

    netTableHue.setDoubleArray([hueMin, hueMax])
    netTableSaturation.setDoubleArray([satMin, satMax])
    netTableValue.setDoubleArray([valMin, valMax])


def restartColor():

    hueMinSlider.set(0)
    hueMaxSlider.set(255)
    satMinSlider.set(0)
    satMaxSlider.set(255)
    valMinSlider.set(0)
    valMaxSlider.set(255)

    setColorParameters(0)


def getTargetYPos():

    global distanceMeasurementsValues
    distance = DistanceInputWidget.get()

    if distance != "":

        TargetYPos = netTableYPos.getNumber(1)
        distance = int(distance)
        distanceMeasurementsValues.append((TargetYPos, distance))
        DistanceInputWidget.delete(0, END)

        putMeasurementsWidgets()


def putMeasurementsWidgets():
    global distanceMeasurementsValues
    global distanceMeasurementsWidgets
    distanceMeasurementsWidgets = []
    for i in range(len(distanceMeasurementsValues)):
        targetYPosInputWidget = Entry(window, width=10)
        targetYPosInputWidget.delete(0, END)
        targetYPosInputWidget.insert(0, distanceMeasurementsValues[i][0])
        targetYPosInputWidget.grid(column=0, row=i+7)
        distanceInputWidget = Entry(window, width=10)
        distanceInputWidget.delete(0, END)
        distanceInputWidget.insert(0, distanceMeasurementsValues[i][1])
        distanceInputWidget.grid(column=1, row=i+7)
        newMeasurement = (targetYPosInputWidget, distanceInputWidget)
        distanceMeasurementsWidgets.append(newMeasurement)
def updateMeasurement(a):
    global distanceMeasurementsValues
    global distanceMeasurementsWidgets
    distanceMeasurementsValues = []
    for i in range(len(distanceMeasurementsWidgets)):
        y = distanceMeasurementsWidgets[i][0].get()
        d = distanceMeasurementsWidgets[i][1].get()
        if y == "":
            y = 0
            distanceMeasurementsWidgets[i][0].delete(0, END)
            distanceMeasurementsWidgets[i][0].insert(0, 0)
        if d == "":
            d = 0
            distanceMeasurementsWidgets[i][1].delete(0, END)
            distanceMeasurementsWidgets[i][1].insert(0, 0)
        if y != "" and y != 0:
            if y[0] == "0" and len(y) > 1:
                distanceMeasurementsWidgets[i][0].delete(0, END)
                distanceMeasurementsWidgets[i][0].insert(0, y[1:])
        if d != "" and d != 0:
            if d[0] == "0" and len(d) > 1:
                distanceMeasurementsWidgets[i][1].delete(0, END)
                distanceMeasurementsWidgets[i][1].insert(0, d[1:])
        distanceMeasurementsValues.append((int(y), int(d)))
def deleteLast():
    global distanceMeasurementsValues
    global distanceMeasurementsWidgets
    if len(distanceMeasurementsValues) != 0:
        distanceMeasurementsValues = distanceMeasurementsValues[:-1]
        print("asa")
        distanceMeasurementsWidgets[-1][0].destroy()
        distanceMeasurementsWidgets[-1][1].destroy()
        distanceMeasurementsWidgets = distanceMeasurementsWidgets[:-1]
        putMeasurementsWidgets()
        
        
def calculateParameters():
    global distanceMeasurementsValues
    n = len(distanceMeasurementsValues)
    if n >= 3:

        Y = []
        D = []

        for measurement in distanceMeasurementsValues:
            Y.append(measurement[0])
            D.append(measurement[1])

        last_position = n-1
        mid_position = int(n/2)
        first_position = 0
        
        def find_x0_function(a):
            return (Y[first_position]-Y[mid_position])/(Y[first_position]-Y[last_position])*(atan(a/D[first_position])-atan(a/D[last_position])) - atan(a/D[first_position]) + atan(a/D[mid_position])
        
        x0_solution = root_scalar(find_x0_function, x0=100, bracket=[1, 500])

        def squared_error_function(x):
            a = x[0]
            b = x[1]
            c = x[2]
            error = 0
            for i in range(n):
                error += (D[i] - (a/np.tan(b*Y[i]+c)))**2
            return error
        
        amin = x0_solution.root-50
        amax = x0_solution.root+50
        a = x0_solution.root
        b = (atan(a/D[first_position]) - atan(a/D[mid_position]))/(Y[first_position]-Y[mid_position])
        c = atan(a/D[first_position])-b*Y[first_position]
        top = [a, b, c]
        m = squared_error_function(np.array([a, b, c]))
        a = amin
        while a < amax:
            x0 = np.array([a, b, c])
            sol = minimize(squared_error_function, x0, bounds=[(amin, amax), (-1, 0), (0.1, 2)])
            if sol.success and sol.fun < m:
                top = sol.x
                m = sol.fun
            a+=0.01
        netTableDistanceParameters.setDoubleArray(top)
        resultLabel.configure(text=str(top))
        print(top)


# creating elements
madeByLabel = Label(window, text="Developed by Pedro Cleto and Breno Bertone")
colorCalibrationLabel = Label(window, text="Color Calibration", font=mediumFont)
hueMinLabel = Label(window, text="HUE MIN")
hueMinSlider = Scale(window, from_=0, to=255, length=200, command=setColorParameters)
hueMaxLabel = Label(window, text="HUE MAX")
hueMaxSlider = Scale(window, from_=0, to=255, length=200, command=setColorParameters)
satMinLabel = Label(window, text="SAT MIN")
satMinSlider = Scale(window, from_=0, to=255, length=200, command=setColorParameters)
satMaxLabel = Label(window, text="SAT MAX")
satMaxSlider = Scale(window, from_=0, to=255, length=200, command=setColorParameters)
valMinLabel = Label(window, text="VAL MIN")
valMinSlider = Scale(window, from_=0, to=255, length=200, command=setColorParameters)
valMaxLabel = Label(window, text="VAL MAX")
valMaxSlider = Scale(window, from_=0, to=255, length=200, command=setColorParameters)
restartButton = Button(window, text="Restart", command=restartColor)
DistanceCalibrationLabel = Label(window, text="Distance Calibration", font=mediumFont)
resultLabel = Label(window, text="")
DistanceInputWidget = Entry(window, width=10)
GetYButton = Button(window, text="Get Y", command=getTargetYPos)
DeleteLastButton = Button(window, text="Delete last", command=deleteLast)
CalculateParametersButton = Button(window, text="Calculate", command=calculateParameters)
# setting them up
getColorParameters()
window.bind("<KeyRelease>", updateMeasurement)
# gridding them
colorCalibrationLabel.grid(column=0, row=2)
hueMinLabel.grid(column=1, row=3)
hueMaxLabel.grid(column=2, row=3)
satMinLabel.grid(column=3, row=3)
satMaxLabel.grid(column=4, row=3)
valMinLabel.grid(column=5, row=3)
valMaxLabel.grid(column=6, row=3)
restartButton.grid(column=0, row=4)
hueMinSlider.grid(column=1, row=4)
hueMaxSlider.grid(column=2, row=4)
satMinSlider.grid(column=3, row=4)
satMaxSlider.grid(column=4, row=4)
valMinSlider.grid(column=5, row=4)
valMaxSlider.grid(column=6, row=4)
DistanceCalibrationLabel.grid(column=0, row=5)
resultLabel.grid(column=0, row=6)
DistanceInputWidget.grid(column=2, row=6)
GetYButton.grid(column=3, row=6)
DeleteLastButton.grid(column=4, row=6)
CalculateParametersButton.grid(column=5, row=6)
madeByLabel.grid(column=0, row=20)
window.mainloop()