#!/usr/bin/env python

import cv2

import matplotlib.pyplot as plt

from robolab_turtlebot import Turtlebot, detector, Rate, get_time

import numpy as np

WINDOW = 'camera'

angular_velocity = 0

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

def draw_center(image, row, col):
    image[row][col][0] = 255
    image[row][col][1] = 255
    image[row][col][2] = 255

    return image

def main():
    turtle.register_bumper_event_cb(bumper_cb)
    turtle.reset_odometry()
    cv2.namedWindow(WINDOW)

    while not turtle.is_shutting_down() and isRunning:
        image = turtle.get_rgb_image()

        # wait for image to be ready
        if image is None:
            continue

        midrow = image.shape[0] / 2
        midcol = image.shape[1] / 2

        blured_image = cv2.blur(image, (10,10))
        hsv = cv2.cvtColor(blured_image, cv2.COLOR_BGR2HSV)

        green_mask = cv2.inRange(hsv,(40, 50, 50), (65, 255, 255) ) # green
        green_filtered, green_count, green_centroids = remove_small_components(green_mask)

        for i in range(0, green_count):
            image = draw_crosshair(image, green_centroids[i][1], green_centroids[i][0], 0, 255, 0)

        if len(green_centroids) == 2:
            center_row = int(min(green_centroids[0][1], green_centroids[1][1]) + abs(green_centroids[0][1] - green_centroids[1][1])/2)
            center_col = int(min(green_centroids[0][0], green_centroids[1][0]) + abs(green_centroids[0][0] - green_centroids[1][0])/2)
            
            image = draw_center(image, center_row, center_col)
            print('Center:  [{}, {}]'.format(center_row, center_col))
                
            global angular_velocity
            print("Distance from center of the screen in px: {}".format(abs(midcol - center_col)))
            if abs(midcol - center_col) > 10:
                if center_col > midcol:
                    angular_velocity = -0.2
                else:
                    angular_velocity = 0.2
            else: 
                angular_velocity = 0
            
            print("Set anguilar_velocity: {}".format(angular_velocity))

        print("-------------------------------")
        print("Found\n{} green objects\n".format(green_count))

        turtle.cmd_velocity(angular = angular_velocity)

        # show image
        cv2.imshow(WINDOW, image)

        cv2.waitKey(1)

    turtle.cmd_velocity(linear = 0)
    turtle.cmd_velocity(angular = 0)

if __name__ == '__main__':
    main()

