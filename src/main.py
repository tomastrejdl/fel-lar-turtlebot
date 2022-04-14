#!/usr/bin/env python

from robolab_turtlebot import Turtlebot
import numpy as np
import cv2

from constants import *
from partitioning import *

isRunning = True
turtle = Turtlebot(rgb=True, pc=True)


def bumper_callback(msg):
    bumper_name = BUMPER_NAMES[msg.bumper] # msg.bumper stores the id of bumper 0:LEFT, 1:CENTER, 2:RIGHT
    bumper_state = BUMPER_STATES[msg.state] # msg.state stores the event 0:RELEASED, 1:PRESSED

    print("{} bumper {}".format(bumper_name, bumper_state))
    if bumper_state == "PRESSED":
        print("Bumber pressed. STOPPING...")
        global isRunning
        isRunning = False
        turtle.cmd_velocity(linear=0)
        turtle.cmd_velocity(angular=0)
        quit()

# Each tick an image is retrieved from robot, analyzed and state is updated accordingly
def next_tick(previous_state, next_gate_color,go_through_gate_timeout):
    print("TICK: ", previous_state, end=" --> ")
    state = previous_state
    image = turtle.get_rgb_image()
    # wait for image to be ready
    if image is None: return

    MIDROW = image.shape[0]/2
    MIDCOL = image.shape[1]/2

    image, filtered, count, centroids = get_objects_for_color(image, next_gate_color)

    center_row = center_col = 0
    if count == 2:
        # If there are 2 pipes in the image
        # find the center point between the two pipes
        image, center_col, center_row = find_center(image, centroids)

        if abs(center_col - MIDCOL) < 30:
            # If we're close to the center move forward
            state = MOVE_FORWARD
        else:
            # If we're NOT close to the center rotate until we're close
            if center_col > MIDCOL:
                state = ROTATE_RIGHT
            else:
                state = ROTATE_LEFT
    else:
        # If there are NOT 2 pipes in the image, keep looking
        if previous_state != LOOKING_FOR_GATE:
            state = GO_THROUGH_GATE
        else:
            state = LOOKING_FOR_GATE
    
    if state == GO_THROUGH_GATE and previous_state == GO_THROUGH_GATE:
        go_through_gate_timeout -= 1
        print("go_through_gate_timeout: ", go_through_gate_timeout)

    if state == GO_THROUGH_GATE and go_through_gate_timeout <= 0:
        state = FINISH

    print(state)
    print("-------------------------------")
    print("Found {} {} objects".format(count, next_gate_color))
    if center_row != 0 and center_col != 0:
        print("Center of gate:  [{}, {}]".format(center_row, center_col))
        print("Distance of gatecenter from center of the screen in px: {}".format(abs(MIDCOL - center_col)))
    print("Setting state to {}".format(state))

    # show image
    cv2.imshow(WINDOW, image)
    cv2.waitKey(1)

    return state, next_gate_color, go_through_gate_timeout


def main():
    print("Starting...")



    turtle.register_bumper_event_cb(bumper_callback)
    turtle.reset_odometry()

    cv2.namedWindow(WINDOW)

    # Default robot state is LOOKING_FOR_GATE
    state = LOOKING_FOR_GATE
    previous_state = LOOKING_FOR_GATE
    next_gate_color = GREEN

    go_through_gate_timeout = 1000

    while not turtle.is_shutting_down() and isRunning and state != FINISH:
        # Look for any gate and update state
        #print("{}, {} = next_tick({}, {})".format(state, next_gate_color, state, next_gate_color))
        
        previous_state = state
        state, next_gate_color,go_through_gate_timeout = next_tick(previous_state, next_gate_color, go_through_gate_timeout)

        # Update velocity based on current state
        if state == LOOKING_FOR_GATE:
            turtle.cmd_velocity(angular=0.4)
        if state == ROTATE_LEFT:
            turtle.cmd_velocity(angular=0.4)
        if state == ROTATE_RIGHT:
            turtle.cmd_velocity(angular=-0.4)
        if state == MOVE_FORWARD:
            turtle.cmd_velocity(linear=0.1)
        if state == GO_THROUGH_GATE:
            turtle.cmd_velocity(linear=0.1)


    # Play finish sound
    turtle.play_sound(1)

    # Stop moving before exiting program
    turtle.cmd_velocity(linear=0)
    turtle.cmd_velocity(angular=0)


if __name__ == "__main__":
    main()
