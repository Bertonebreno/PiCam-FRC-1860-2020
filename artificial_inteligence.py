import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from time import time
# entrar com 3 matrizes (frame RGB)
# sair com 3 numeros

w = 480
h = 270

def func(X, parameters):
    list_of_columns = np.split(parameters, 3*w*h*np.array([1, 2, 3]))
    A = np.stack(list_of_columns[:-1], axis=1)
    B = list_of_columns[-1]
    R = np.dot(A.T, X)+B
    x, y, r = R[0], R[1], R[2]
    return x, y, r

def loading_training_dataset():
    images = []
    labels = []
    images_list = os.listdir("training_dataset/images")
    quantity_images = len(images_list)
    labels_list = os.listdir("training_dataset/labels")
    quantity_labels = len(labels_list)
    if quantity_images != quantity_labels:
        print("wrong quantities")
        exit(0)
    n = quantity_images
    for i in range(1, n):
        image = cv2.imread("training_dataset/images/"+str(i)+".jpeg")
        images.append(image)
        label_file = open("training_dataset/labels/"+str(n)+".txt", "r")
        content = label_file.read()
        new_label = list(map(float, content.split()))
        labels.append(new_label)
        label_file.close()
    return images, labels

cap = cv2.VideoCapture("http://131.173.8.23/mjpg/video.mjpg")

images, labels = loading_training_dataset()

# x0_parameters = np.random.rand(9*w*h+3)*0.00001
parameters = np.load("perfect_params.npy")

def error_squared(parameters):
    print("calculating error")
    error = 0
    for i in range(len(images)):
        X = np.reshape(images[i], (3*w*h))
        x, y, r = func(X, parameters)
        error += (labels[i][0] - x)**2
        error += (labels[i][1] - y)**2
        error += (labels[i][2] - r)**2
    print(error)
    return error

def error_derivative(parameters):
    print("calculating derivative")
    dparameters = np.zeros(9*w*h+3)
    for j in range(len(images)):
        X = np.reshape(images[j], (3*w*h))
        x, y, r = func(X, parameters)
        x_error = labels[j][0]-x
        y_error = labels[j][1]-y
        r_error = labels[j][2]-r
        range_size = 3*w*h
        split_points = np.array([range_size, 2*range_size, 3*range_size])
        a_dparameters, b_dparameters, c_dparameters, d_dparameters = np.split(dparameters, split_points)
        a_dparameters -= 2*x_error*X
        b_dparameters -= 2*y_error*X
        c_dparameters -= 2*r_error*X
        d_dparameters -= x_error + y_error + r_error
        dparameters = np.concatenate([a_dparameters, b_dparameters, c_dparameters, d_dparameters], axis=0)
    return dparameters

def minimize_callback(x):
    error = error_squared(x)
    if error < 0.1:
        np.save("perfect_params", x)
        print("params saved!!")
        final_time = time()
        print("time:", final_time-initial_time)
        exit(0)

initial_time = time()

# sol = minimize(error_squared, 
#     x0_parameters, 
#     method='CG', 
#     jac=error_derivative, 
#     callback=minimize_callback)
while True:
    ret, frame = cap.read()
    new_frame = cv2.resize(frame, (w, h))
    X = np.reshape(new_frame, (3*w*h))
    result = func(X, parameters)
    x = result[0]
    y = result[1]
    r = result[2]
    print("x:",x)
    print("y:",y)
    print("r:",r)
    cv2.circle(new_frame, (int(x), int(y)), int(r), (0, 0, 255), 4)
    cv2.circle(new_frame, (int(x), int(y)), 2, (0, 0, 255), 4)
    cv2.imshow("image", new_frame)
    if cv2.waitKey(1) == 27:
        exit(0)