from math import tan
import matplotlib.pyplot as plt
import scipy.optimize as opt

x0 = 5000
a = [-1650, 0.00001, 0, 0]
n = len(a)
deg = len(a)-1
b = -8.476615985292078e-04
c = 0.7222027116421984
def d(x):
  def f(d):
    xs = []
    for i in range(n):
      xs.append(d**i)
    r = 0
    for i in range(n):
      r += xs[i]*a[i]
    return r
  def df(d):
    xs = [0]
    for i in range(1, n):
      xs.append(i*d**(i-1))
    r = 0
    for i in range(n):
      r += xs[i]*a[i]
    return r
  def dfinder(d):
    d = int(d)
    return d*tan(b*x+c)+d*df(d)+f(d)-tan(b*x+c)*f(d)*df(d)
  sol = opt.root(dfinder, x0)
  return sol.x[0]
xs = []
ds = []
i = 0
while i < 700:
  xs.append(i)
  ds.append(d(i))
  print(i, ds[int(i)])
  i+=0.5
plt.ylim(-10000, 10000)
plt.plot(xs, ds)
plt.show()
plt.savefig("grafico.png")