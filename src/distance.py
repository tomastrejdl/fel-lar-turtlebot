#!/usr/bin/env python

from robolab_turtlebot import Turtlebot
import numpy as np
import cv2

from constants import *
from partitioning import *

def euclid_norm(x, y, z):
    return np.sqrt(x*x + y*y + z*z)

def pc_to_distance(pc, row, column):
    x = pc[row][column][0]
    y = pc[row][column][1]
    z = pc[row][column][2]
    return euclid_norm(x, y, z)

def get_distance_to_closest_object_of_color(image, color):
    image, filtered, count, centroids = get_objects_for_color(image, color)

    print(centroids)

    return 0
    
def find_closest_gate_color(image):
    red_distance = get_distance_to_closest_object_of_color(image, RED)
    blue_distance = get_distance_to_closest_object_of_color(image, BLUE)

    if red_distance < blue_distance:
        return RED
    else:
        return BLUE

# def camera_to_world(x, y, z):
#     # x_c ... vector of camera coordinates
#     x_c = np.array(x, y, z)

#     # x_w ... vector of world coordinates
#     x_w = np.matmul(t_o, t_c, x_c)