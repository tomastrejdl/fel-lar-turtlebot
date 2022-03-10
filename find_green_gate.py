#!/usr/bin/env python

import cv2

import matplotlib.pyplot as plt

from robolab_turtlebot import Turtlebot, detector, Rate, get_time

import numpy as np

WINDOW = 'camera'

angular_velocity = 0
linear_velocity = 0

LOOKING_FOR_GATE = 0
MOVE = 1
ROTATE = 2

isRunning = True

turtle = Turtlebot(rgb=True, pc=True)
rate = Rate(10)

# Names bumpers and events
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']

def forceStop():
    print('FORCE STOPPING')
    global isRunning
    isRunning = False
    turtle.cmd_velocity(linear = 0)
    turtle.cmd_velocity(angular = 0)
    quit()

def bumper_cb(msg):
    """Bumber callback."""
    # msg.bumper stores the id of bumper 0:LEFT, 1:CENTER, 2:RIGHT
    bumper = bumper_names[msg.bumper]

    # msg.state stores the event 0:RELEASED, 1:PRESSED
    state = state_names[msg.state]

    # Print the event
    print('{} bumper {}'.format(bumper, state))
    if state == 'PRESSED':
        print('Bumper pressed Stopping')
        forceStop()

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

def draw_center(image, x, y):
    image[x][y][0] = 255
    image[x][y][1] = 255
    image[x][y][2] = 255

    return image

def main():
    turtle.register_bumper_event_cb(bumper_cb)
    turtle.reset_odometry()
    cv2.namedWindow(WINDOW)

    show_crosshair = 0

    while not turtle.is_shutting_down() and isRunning:

        image = turtle.get_rgb_image()

        # wait for image to be ready
        if image is None:
            continue

        midrow = image.shape[0] / 2
        midcol = image.shape[1] / 2

        blured_image = cv2.blur(image, (10,10))

        if show_crosshair == 1:
            image = draw_crosshair(image, midrow, midcol, 255, 255, 0)
        

        #print("BGR: {}\nHSV: {}".format(image[int(midrow)][int(midcol)], hsv[int(midrow)][int(midcol)]))


        state = LOOKING_FOR_GATE
        

        hsv = cv2.cvtColor(blured_image, cv2.COLOR_BGR2HSV)

        red_mask = cv2.inRange(hsv,(0, 170, 20), (10, 255, 255) ) # red
        green_mask = cv2.inRange(hsv,(40, 50, 50), (65, 255, 255) ) # green
        blue_mask = cv2.inRange(hsv,(92, 180, 50), (100, 255, 255) ) # blue

        red_filtered, red_count, red_centroids = remove_small_components(red_mask)
        green_filtered, green_count, green_centroids = remove_small_components(green_mask)
        blue_filtered, blue_count, blue_centroids = remove_small_components(blue_mask)

        for i in range(0, red_count):
            image = draw_crosshair(image, int(red_centroids[i][1]), int(red_centroids[i][0]), 255, 0, 0)

        green_objects = []
        for i in range(0, green_count):
            green_center_x = int(green_centroids[i][0])
            green_center_y = int(green_centroids[i][1])
            green_objects.append([green_center_y, green_center_x])
            image = draw_crosshair(image, green_center_y, green_center_x, 0, 255, 0)

        if len(green_objects) == 2:
            center_x = int(min(green_objects[0][0], green_objects[1][0]) + abs(green_objects[0][0] - green_objects[1][0])/2)
            center_y = int(min(green_objects[0][1], green_objects[1][1]) + abs(green_objects[0][1] - green_objects[1][1])/2)
            
            image = draw_center(image, center_x, center_y)
            print('Center:  [{}, {}]'.format(center_x, center_y))
                
            print("Distance from center of the screen in px: {}".format(abs(midcol - center_y)))
            global angular_velocity
            global linear_velocity
            print("Set angular_velocity: {}".format(angular_velocity))
            print("Set linear_velocity: {}".format(linear_velocity))
            #green_flag = 0
            if abs(center_y - 320) > 10:
                linear_velocity = 0
                if center_y > 320:
                    angular_velocity = -0.2
                    state = ROTATE
                else:
                    angular_velocity = 0.2
                    state = ROTATE
            else: 
                angular_velocity = 0
                linear_velocity = 0.1
                state = MOVE

                

        

        for i in range(0, blue_count):
            image = draw_crosshair(image, int(blue_centroids[i][1]), int(blue_centroids[i][0]), 0, 0, 255)

        print("-------------------------------")
        print("Found\n{} red objects\n{} green objects\n{} blue objects".format(red_count, green_count, blue_count))

        #red_contours, r_hierarchy = cv2.findContours(red_filtered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #green_contours, g_hierarchy = cv2.findContours(green_filtered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #blue_contours, b_hierarchy = cv2.findContours(blue_filtered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if state == LOOKING_FOR_GATE:
            turtle.cmd_velocity(angular = 0.2)
       
        if state == ROTATE:
            turtle.cmd_velocity(angular = angular_velocity)

        if state == MOVE:
            turtle.cmd_velocity(linear = linear_velocity)
        rate.sleep()


        # show image
        cv2.imshow(WINDOW, image)

        #cv2.imshow("blue", blue fitlered)
        #cv2.imshow("red", red_filtered)
        # cv2.imshow("green", green_filtered)
        cv2.waitKey(1)

    turtle.cmd_velocity(linear = 0)
    turtle.cmd_velocity(angular = 0)

if __name__ == '__main__':
    main()

