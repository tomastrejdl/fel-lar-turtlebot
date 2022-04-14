#!/usr/bin/env python

from robolab_turtlebot import Turtlebot
import numpy as np
import cv2

from constants import *

def euclid_norm(x, y, z):
    return np.sqrt(x*x + y*y + z*z)

def pc_to_distance(pc, row, column):
    x = pc[row][column][0]
    y = pc[row][column][1]
    z = pc[row][column][2]
    return euclid_norm(x, y, z)

def find_closest_gate_color():
    # TODO: Implement this
    return RED