import math

diagonalFOV = float(input("Diagonal FOV: "))
horizontalAspect = float(input("Horizontal Resolution: "))
verticalAspect = float(input("Vertical Resolution: "))

diagonalFOV = diagonalFOV*math.pi/180
diagonalAspect = math.sqrt(horizontalAspect**2 + verticalAspect**2)

horizontalFOV = math.atan((math.tan(diagonalFOV/2)*horizontalAspect/diagonalAspect))*360/math.pi
verticalFOV = math.atan((math.tan(diagonalFOV/2)*verticalAspect/diagonalAspect))*360/math.pi

print("Horizontal FOV: %s" % horizontalFOV)
print("Vertical FOV: %s" % verticalFOV)

print("Focal Length: %s" % (horizontalAspect/(2*math.tan(horizontalFOV*math.pi/360))))
print("Focal Length: %s" % (verticalAspect/(2*math.tan(verticalFOV*math.pi/360))))
print("Bertone, Breno")