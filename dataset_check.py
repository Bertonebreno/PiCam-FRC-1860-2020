import cv2
import os
import numpy as np
import matplotlib.pyplot as plt

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
        label_file = open("training_dataset/labels/"+str(i)+".txt", "r")
        content = label_file.read()
        new_label = list(map(float, content.split()))
        # new_label[0] /= w
        # new_label[1] /= h
        # new_label[2] /= w
        labels.append(new_label)
        label_file.close()
    images = np.array(images)
    labels = np.array(labels)
    return images, labels

images, labels = loading_training_dataset()

w = 480
h = 270

def onclick(event):
    plt.close()

for i in range(len(images)):
    image = images[i]
    label = labels[i]
    x, y, r = label[0], label[1], label[2]
    print(x, y, r)
    cv2.circle(image, (int(x), int(y)), int(r), (0, 0, 255), 4)
    cv2.circle(image, (int(x), int(y)), 2, (0, 0, 255), 4)
    fig,ax = plt.subplots()
    ax.imshow(image)
    fig.canvas.mpl_connect('button_press_event', onclick)
    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())
    plt.show()