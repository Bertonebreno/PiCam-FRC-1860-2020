import numpy as np

x = [158, 283, 356, 435, 468, 475]
d = [1860, 2780, 3700, 5510, 6430, 7410]

n = len(x)-1
if (len(x) != len(d)):
    print("different lengths")

arr = []
for i in range(0, n+1):
    line = []
    for j in range(n, -1, -1):
        line.append(x[i]**j)
    arr.append(line)
M = np.array(arr)
D = np.array(d)
X = np.linalg.solve(M, D)

print(X)