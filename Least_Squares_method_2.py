import numpy as np
from scipy.optimize import least_squares

D = [2445, 3705, 4775, 5758, 7356]
Y = [143, 254, 305, 335, 370]
n = len(D)
def func(x):
    a = x[0]
    b = x[1]
    c = x[2]
    d = x[3]
    vec = []
    for i in range(n):
        val = D[i] - (a/np.tan(b*Y[i]+c) + d)
        vec.append(val)
    arr = np.array(vec)
    return arr

x0 = np.array([1182.1858360152085, -0.001280039613577564, 0.63266083803553772, 200])
res_1 = least_squares(func, x0)
print(res_1.x)