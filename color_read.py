#!/usr/bin/env python

import cv2

import matplotlib.pyplot as plt

from robolab_turtlebot import Turtlebot, detector

import numpy as np

from depth import euclid_norm
from depth import pc_to_distance

WINDOW = 'camera'

def get_normalized_bgr(b, g, r):
    norm_r = r/(r+g+b)
    norm_g = g/(r+g+b)
    norm_b = b/(r+g+b)
    return norm_b, norm_g, norm_r

def remove_small_components(color_mask):
    n_comp, output, stats, centroids = cv2.connectedComponentsWithStats(color_mask, connectivity=8)

    sizes = stats[1:, -1] 
    n_comp = n_comp - 1

    min_size = 1000  

    new = np.zeros((output.shape))
    new_n_components = 0
    new_centroids = []
    for i in range(0, n_comp):
        if sizes[i] >= min_size:
            new_centroids.append(centroids[i+1])
            new[output == i + 1] = 255
            new_n_components += 1
    return new, new_n_components, new_centroids


def draw_crosshair(image, crosshair_row, crosshair_col, R, G, B):
    for row in range(0, image.shape[0]):
        for col in range(0, image.shape[1]):
            if abs(row - crosshair_row) < 1 or abs (col - crosshair_col) < 1:
                image[row][col][0] = B
                image[row][col][1] = G
                image[row][col][2] = R
    return image

def main():

    turtle = Turtlebot(rgb=True, pc=True)
    cv2.namedWindow(WINDOW)


    show_crosshair = 0

    while not turtle.is_shutting_down():

        image = turtle.get_rgb_image()
        pc = turtle.get_point_cloud()
        # wait for image to be ready
        if image is None or pc is None:
            continue

        midrow = image.shape[0] / 2
        midcol = image.shape[1] / 2

        blured_image = cv2.blur(image, (10,10))

        if show_crosshair == 1:
            image = draw_crosshair(image, midrow, midcol, 255, 255, 0)

        hsv = cv2.cvtColor(blured_image, cv2.COLOR_BGR2HSV)

        red_mask = cv2.inRange(hsv,(0, 170, 20), (10, 255, 255) ) # red
        green_mask = cv2.inRange(hsv,(30, 50, 50), (80, 255, 255) ) # green
        blue_mask = cv2.inRange(hsv,(92, 180, 50), (100, 255, 255) ) # blue

        red_filtered, red_count, red_centroids = remove_small_components(red_mask)
        green_filtered, green_count, green_centroids = remove_small_components(green_mask)
        blue_filtered, blue_count, blue_centroids = remove_small_components(blue_mask)

        for i in range(0, red_count):
            image = draw_crosshair(image, int(red_centroids[i][1]), int(red_centroids[i][0]), 255, 0, 0)
            dist = pc_to_distance(pc, int(red_centroids[i][1]), int(red_centroids[i][0]))
            image = cv2.putText(image, '{:.2f}'.format(dist), (int(red_centroids[i][1]), int(red_centroids[i][0])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
            print("Red centroid n {} is {:.2f} far".format(i, dist))

        for i in range(0, green_count):
            image = draw_crosshair(image, int(green_centroids[i][1]), int(green_centroids[i][0]), 0, 255, 0)
            dist = pc_to_distance(pc, int(green_centroids[i][1]), int(green_centroids[i][0]))
            image = cv2.putText(image, '{:.2f}'.format(dist), (int(green_centroids[i][1]), int(green_centroids[i][0])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
            print("Green centroid n {} is {:.2f} far".format(i, dist))

        for i in range(0, blue_count):
            image = draw_crosshair(image, int(blue_centroids[i][1]), int(blue_centroids[i][0]), 0, 0, 255)
            dist = pc_to_distance(pc, int(blue_centroids[i][1]), int(blue_centroids[i][0]))
            image = cv2.putText(image, '{:.2f}'.format(dist), (int(blue_centroids[i][1]), int(blue_centroids[i][0])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
            print("Blue centroid n {} is {:.2f} far".format(i, dist))

        print("-------------------------------")
        print("Found\n{} red objects\n{} green objects\n{} blue objects".format(red_count, green_count, blue_count))

        




        cv2.imshow(WINDOW, image)

        #cv2.imshow("blue", blue fitlered)
        #cv2.imshow("red", red_filtered)
        cv2.imshow("green", green_filtered)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()

