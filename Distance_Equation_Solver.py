from math import atan
from time import time

xs = [610, 546, 199]
ds = [687, 530, 154]

def f(a):
  return (xs[0]-xs[1])/(xs[0]-xs[2])*(atan(a/ds[0])-atan(a/ds[2])) - atan(a/ds[0]) + atan(a/ds[1])

x = 10000
vel = 1
passos = 0

inicial = time()

while True:
  passos += 1
  print(x, f(x))
  if f(x) > 1.0e-10:
    x -= x*f(x)*vel
  if f(x) < 1.0e-10 and f(x) > 0:
    break
  if f(x) < 0:
    x += abs(x*f(x)*vel)

final = time()

print(x, f(x))
print("passos =", passos)
print("tempo =", final - inicial, "segundos")
#a = 136-89
a = x
b = (atan(a/ds[0]) - atan(a/ds[1]))/(xs[0]-xs[1])
c = atan(a/ds[0])-b*xs[0]
print("a =", a)
print("b =", b)
print("c =", c)