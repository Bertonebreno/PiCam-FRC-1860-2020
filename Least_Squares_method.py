from math import tan, sin

D = [2445, 3705, 4775, 5758, 7356]
Y = [143, 254, 305, 335, 370]
n = len(D)
# b = -0.001280039613577564
# c = 0.6326608380355377
def eq1(b, c):
    sum1 = 0
    for i in range(n):
        sum1 += Y[i]/(tan(b*Y[i]+c)*(sin(b*Y[i]+c))**2)
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

# calc a
sum1 = 0
for i in range(n):
    sum1 += D[i]/tan(b*Y[i]+c)
sum2 = 0
for i in range(n):
    sum2 += 1/(tan(b*Y[i]+c))**2
a = sum1/sum2
print("a:", a)

