#!/usr/bin/env python


import numpy as np
import math

from constants import *
from partitioning import *

def euclid_norm(x, y, z):
    return np.sqrt(x*x + y*y + z*z)

def pc_to_distance(pc, row, column):
    x_square = np.array([])
    y_square = np.array([])
    z_square = np.array([])

    for i in range(-1, 2):
        for j in range(-1, 2):
            x_square = np.append(x_square, pc[row-i][column-j][0])
            y_square = np.append(y_square, pc[row-i][column-j][1])
            z_square = np.append(z_square, pc[row-i][column-j][2])
    x = np.mean(x_square[np.isfinite(x_square)])
    y = np.mean(y_square[np.isfinite(y_square)])
    z = np.mean(z_square[np.isfinite(z_square)])
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

def get_distance_to_closest_object_of_color(image, pc, color, min_size):
    _, _, _, centroids = get_objects_for_color(image, color, min_size)
    # print(f'{color} centroids: {centroids}')

    min_distance = math.inf
    for c in centroids:
        _, _, _, distance = pc_to_distance(pc, int(c[1]), int(c[0]))
        min_distance = distance if distance < min_distance else min_distance
    # print(f'Closest {color} object distance: {min_distance}')

    return min_distance
    
def find_closest_gate_color(image, pc, min_size):
    red_distance = get_distance_to_closest_object_of_color(image, pc, RED, min_size)
    blue_distance = get_distance_to_closest_object_of_color(image, pc, BLUE, min_size)

    return RED if red_distance < blue_distance else BLUE
