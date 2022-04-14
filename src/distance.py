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
    return x, y, z, euclid_norm(x, y, z)

def get_coords(pc, row, column):
    x = pc[row][column][0]
    y = pc[row][column][1]
    z = pc[row][column][2]
    return x, y, z

def get_intersections(x0, y0, r0, x1, y1, r1):
    # circle 1: (x0, y0), radius r0
    # circle 2: (x1, y1), radius r1

    d=math.sqrt((x1-x0)**2 + (y1-y0)**2)

    # non intersecting
    if d > r0 + r1 :
        return None
    # One circle within other
    if d < abs(r0-r1):
        return None
    # coincident circles
    if d == 0 and r0 == r1:
        return None
    else:
        a=(r0**2-r1**2+d**2)/(2*d)
        h=math.sqrt(r0**2-a**2)
        x2=x0+a*(x1-x0)/d   
        y2=y0+a*(y1-y0)/d   
        x3=x2+h*(y1-y0)/d     
        y3=y2-h*(x1-x0)/d 

        x4=x2-h*(y1-y0)/d
        y4=y2+h*(x1-x0)/d
        
        return (x3, y3, x4, y4)

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
