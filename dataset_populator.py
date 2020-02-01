import cv2
import numpy as np
import os
from time import sleep
import matplotlib.pyplot as plt
# pegar stream da camera do robo
cap = cv2.VideoCapture("http://131.173.8.23/mjpg/video.mjpg")

w = 480
h = 270

def ball_identifier(frame):
    x = int(input("x: "))
    y = int(input("y: "))
    r = int(input("r: "))
    return frame, x, y, r-x

def add_new_image(frame):
    images_list = os.listdir("training_dataset/images")
    quantity_images = len(images_list)
    
    if quantity_images == 0:
        n = 1
    else:
        for i in range(quantity_images):
            images_list[i] = int(images_list[i][:-5])
        n = max(images_list)+1
    
    cv2.imwrite("training_dataset/images/"+str(n)+".jpeg", frame)

def add_new_label(x, y, r):
    labels_list = os.listdir("training_dataset/labels")
    quantity_labels = len(labels_list)
    
    if quantity_labels == 0:
        n = 1
    else:
        for i in range(quantity_labels):
            labels_list[i] = int(labels_list[i][:-4])
        n = max(labels_list)+1

    label_file = open("training_dataset/labels/"+str(n)+".txt", "w")
    label_file.write(str(x)+" "+str(y)+" "+str(r))
    label_file.close()

quantity_of_clicks = 0
x0, y0, x1, y1 = 0, 0, 0, 0

def onclick(event):
    global x0, y0, x1, y1, quantity_of_clicks
    quantity_of_clicks += 1
    if quantity_of_clicks == 2:
        x1, y1 = event.xdata, event.ydata
        quantity_of_clicks = 0
        plt.close()
        
    else:
        x0, y0 = event.xdata, event.ydata

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (w, h))
    images_list = os.listdir("training_dataset/images")
    labels_list = os.listdir("training_dataset/labels")
    print(len(labels_list))
    if len(images_list) != len(labels_list):
        print("some problem with the training dataset")
        exit(0)
    fig,ax = plt.subplots()
    ax.imshow(frame)
    fig.canvas.mpl_connect('button_press_event', onclick)
    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())
    plt.show()
    x, y, r = x0, y1, x1-x0
    print(x, y, r)
    add_new_image(frame)
    add_new_label(x, y, r)
    
    