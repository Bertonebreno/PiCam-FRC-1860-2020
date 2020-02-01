from math import tan
D = [190,287,367,439,500]
Y = [159,362,464,538,575]
n = len(D)
parameters = [ 1.64719537e+02, -9.45465790e-04,  8.63562414e-01]
def func(x):
    a = parameters[0]
    b = parameters[1]
    c = parameters[2]
    return a/tan(b*x+c)
for i in range(n):
    de = func(Y[i])
    print("y: {} dr: {} de: {} er: {}".format(Y[i], D[i], de, de-D[i]))