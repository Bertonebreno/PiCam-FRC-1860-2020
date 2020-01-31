from math import atan
from time import time
from scipy.optimize import root_scalar

<<<<<<< HEAD
ds = [490,350,210]
xs = [500,373,125]
=======

ds = [398, 544, 747]
xs = [447, 555, 640]

>>>>>>> e2045ebfd5cac8d127d0956e5ac72d778ba3f294

def func(a):
  return (xs[0]-xs[1])/(xs[0]-xs[2])*(atan(a/ds[0])-atan(a/ds[2])) - atan(a/ds[0]) + atan(a/ds[1])

sol = root_scalar(func, x0=10, bracket=[1, 10000])
a = sol.root
b = (atan(a/ds[0]) - atan(a/ds[1]))/(xs[0]-xs[1])
c = atan(a/ds[0])-b*xs[0]
print([a, b, c])
print("a =", a)
print("b =", b)
print("c =", c)