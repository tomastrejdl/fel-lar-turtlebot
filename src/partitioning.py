import numpy as np
import cv2

from constants import RED, GREEN, BLUE 
from drawing import draw_crosshairs_for_color, draw_center

def remove_small_components(color_mask):
    n_comp, output, stats, centroids = cv2.connectedComponentsWithStats(color_mask, connectivity=8)

    sizes = stats[1:, -1]
    n_comp = n_comp - 1

    min_size = 6000

    new = np.zeros((output.shape))
    new_n_components = 0
    new_centroids = []
    for i in range(0, n_comp):
        if sizes[i] >= min_size:
            print(sizes[i])
            new_centroids.append(centroids[i + 1])
            new[output == i + 1] = 255
            new_n_components += 1
    return new, new_n_components, new_centroids

def get_objects_for_color(image, color):
    blured_image = cv2.blur(image, (10, 10))
    hsv = cv2.cvtColor(blured_image, cv2.COLOR_BGR2HSV)

    if color == RED: mask = cv2.inRange(hsv, (0, 170, 20), (10, 255, 255))
    if color == GREEN: mask = cv2.inRange(hsv, (30, 50, 50), (80, 255, 255))
    if color == BLUE: mask = cv2.inRange(hsv, (92, 180, 50), (100, 255, 255))

    filtered, count, centroids =  remove_small_components(mask)

    image = draw_crosshairs_for_color(image, count, centroids, color)

    return image, filtered, count, centroids

def find_center(image, centroids):
    center_row = int(min(centroids[0][0], centroids[1][0]) + abs(centroids[0][0] - centroids[1][0]) / 2)
    center_col = int(min(centroids[0][1], centroids[1][1]) + abs(centroids[0][1] - centroids[1][1]) / 2)
    image = draw_center(image, center_row, center_col)

    return image, center_row, center_col