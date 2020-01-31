from math import tan, sin
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from scipy.optimize import root

D = [2445, 3705, 4775, 5758, 7356]
Y = [143, 254, 305, 335, 370]
n = len(D)
b = -0.001280039613577564
c = 0.6326608380355377
x0 = [b, c]
def eq1(b, c):
    sum1 = 0
    for i in range(n):
        sum1 += Y[i]/((tan(b*Y[i]+c)*(sin(b*Y[i]+c))**2))
    sum2 = 0
    for i in range(n):
        sum2 += D[i]/tan(b*Y[i]+c)
    sum3 = 0
    for i in range(n):
        sum3 += D[i]*Y[i]/tan(b*Y[i]+c)
    sum4 = 0
    for i in range(n):
        sum4 += 1/(tan(b*Y[i]+c))**2
    return sum1*sum2-sum3*sum4

def eq2(b, c):
    sum1 = 0
    for i in range(n):
        sum1 += 1/(tan(b*Y[i]+c)*(sin(b*Y[i]+c))**2)
    sum2 = 0
    for i in range(n):
        sum2 += D[i]/tan(b*Y[i]+c)
    sum3 = 0
    for i in range(n):
        sum3 += D[i]/tan(b*Y[i]+c)
    sum4 = 0
    for i in range(n):
        sum4 += 1/(tan(b*Y[i]+c))**2
    return sum1*sum2-sum3*sum4
def fun(x):
    b = x[0]
    c = x[1]
    y = [0, 0]
    y[0] = eq1(b, c)
    y[1] = eq2(b, c)
    r = np.array(y)
    return r
print("eq1:", eq1(b, c))
print("eq2:", eq2(b, c))
sol = root(fun, x0)
print(sol.x)
b = sol.x[0]
c = sol.x[1]
# calc a
sum1 = 0
for i in range(n):
    sum1 += D[i]/tan(b*Y[i]+c)
sum2 = 0
for i in range(n):
    sum2 += 1/(tan(b*Y[i]+c))**2
a = sum1/sum2
print("a:", a)