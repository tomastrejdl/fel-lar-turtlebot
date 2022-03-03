#!/usr/bin/env python

import cv2

import matplotlib.pyplot as plt

from robolab_turtlebot import Turtlebot, detector

WINDOW = 'camera'

def get_normalized_bgr(b, g, r):
    norm_r = r/(r+g+b)
    norm_g = g/(r+g+b)
    norm_b = b/(r+g+b)
    return norm_b, norm_g, norm_r

def main():

    turtle = Turtlebot(rgb=True, pc=True)
    cv2.namedWindow(WINDOW)


    show_crosshair = 1

    while not turtle.is_shutting_down():
        # get point cloud
        image = turtle.get_rgb_image()

        # wait for image to be ready
        if image is None:
            continue

        blured_image = cv2.blur(image, (10,10))

        hsv = cv2.cvtColor(blured_image, cv2.COLOR_BGR2HSV)

        blue_mask = cv2.inRange(hsv,(94, 180, 50), (99, 255, 255) ) # blue
        red_mask = cv2.inRange(hsv,(0, 170, 20), (7, 255, 255) ) # red
        green_mask = cv2.inRange(hsv,(40, 50, 50), (65, 255, 255) ) # green

        midrow = image.shape[0] / 2
        midcol = image.shape[1] / 2
        print("-------------------")

        #print("GBR: {}\nHSV: {}".format(image[int(midrow)][int(midcol)], hsv[int(midrow)][int(midcol)]))

        #contours, hierarchy = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #print(len(contours))
        
        # out = cv2.connectedComponentsWithStats(bin_mask.astype(np.uint8))

        '''
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4,4))
        green_rects = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel, iterations=1)
        red_rects = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel, iterations=2)
        blue_rects = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel, iterations=2)
        '''
        '''
        green_rects = cv2.blur(green_rects, (3,3))
        red_rects = cv2.blur(red_rects, (3,3))
        blue_rects = cv2.blur(blue_rects, (3,3))
        '''

        contours = []
        green_contours, g_hierarchy = cv2.findContours(green_rects, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        red_contours, r_hierarchy = cv2.findContours(red_rects, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        blue_contours, b_hierarchy = cv2.findContours(blue_rects, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        

        
        green_found = len(green_contours)
        red_found = len(red_contours)
        blue_found = len(blue_contours)
        print("Found\n{} green objects\n{} red objects\n{} blue objects".format(green_found, red_found, blue_found))


    
        if show_crosshair == 1:
            for row in range(0, image.shape[0]):
                for col in range(0, image.shape[1]):
                    if abs(row - midrow) < 1 or abs (col - midcol) < 1:
                        image[row][col][0] = 0
                        image[row][col][1] = 255
                        image[row][col][2] = 255


        # show image
        cv2.imshow(WINDOW, image)
        #cv2.imshow("flex", flex_mask)
        cv2.imshow("blue", blue_mask)
        cv2.imshow("red", red_mask)
        cv2.imshow("green", green_mask)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()

