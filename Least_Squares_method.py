import numpy as np
from scipy.optimize import minimize, root_scalar
from math import atan
from time import time

D = [201.5, 180, 153, 135, 118, 94]
Y = [638, 577, 473.5, 394, 322, 221]
n = len(D)

initial_time = time()

last_position = n-1
mid_position = int(n/2)
first_position = 0

def find_x0_function(a):
  return (Y[first_position]-Y[mid_position])/(Y[first_position]-Y[last_position])*(atan(a/D[first_position])-atan(a/D[last_position])) - atan(a/D[first_position]) + atan(a/D[mid_position])

# Xs = []
# Ys = []
# for i in range(0, 1000):
#     Xs.append(i)
#     Ys.append(find_x0_function(i))
# plt.plot(Xs, Ys)
# plt.show()

sol1 = root_scalar(find_x0_function, x0=100, bracket=[1, 500])
#1.64719536e+02 -9.45465789e-04  8.63562412e-01
#1.64722700e+02 -9.45494432e-04  8.63583089e-01
def squared_error_function(x):
    a = x[0]
    b = x[1]
    c = x[2]
    error = 0
    for i in range(n):
        error += (D[i] - (a/np.tan(b*Y[i]+c)))**2
    return error

amin = sol1.root-50
amax = sol1.root+50
a = sol1.root
b = (atan(a/D[first_position]) - atan(a/D[mid_position]))/(Y[first_position]-Y[mid_position])
c = atan(a/D[first_position])-b*Y[first_position]

top = [a, b, c]
m = squared_error_function([a, b, c])
a = amin
while a < amax:
    x0 = np.array([a, b, c])
    sol2 = minimize(squared_error_function, x0, bounds=[(amin, amax), (-1, 0), (0.1, 2)])
    if sol2.success:
        #print("\n", round(a-amin, 2), "/", round(amax-amin, 2))
        #print("error: ", round(sol2.fun, 6))
        #print("minimum:", round(m, 6))
        #print(sol2.x)
        if sol2.fun < m:
            top = sol2.x
            m = sol2.fun
        print(a-amin/amax-amin)
    else:
        if a % 10 == 0:
            print(a, "n rolou")
    a += 0.01
print("top:")
print(top)
final_time = time()
print("time: {}".format(final_time-initial_time))