import numpy as np

x = [477, 459, 416, 360, 177]
d = [7140, 6183, 5060, 3620, 1960]

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