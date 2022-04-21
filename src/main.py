#!/usr/bin/env python

from robolab_turtlebot import Turtlebot
import numpy as np
import cv2

from distance import *
from constants import *
from partitioning import *
from rotate_translate import *
from angle_dist_angle import *

end_angle = 0
end_angle2 = 0
end_distance = 0
target = 1
distance_and_angle = []


isRunning = True
turtle = Turtlebot(rgb=True, pc=True)

motors_enabled = True

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
def next_tick(previous_state, next_gate_color, timeout):
    state = previous_state
    image = turtle.get_rgb_image()
    pc = turtle.get_point_cloud()

    # wait for image to be ready
    if image is None: return

    MIDROW = image.shape[0]/2
    MIDCOL = image.shape[1]/2

    image, filtered, count, centroids = get_objects_for_color(image, next_gate_color)
    cv2.imshow("mask", filtered)
    print(count)
    global end_angle
    global end_angle2
    global end_distance
    global target
    global distance_and_angle

    center_row = center_col = 0

    angle_range = 30
    

    if state == LOSE_CENTER:
        while filtered[MIDCOL][MIDROW] != 0:
            state = ROTATE_RIGHT
        rotate_by_angle(turtle, "RIGHT", math.radians(5) - 0.01)
        state = ROTATE_AND_MEASURE

    if state == ROTATE_AND_MEASURE:
        '''
        rotate_by_angle(turtle, "LEFT", math.radians(angle_range) - 0.01)
        x, y, current_angle = turtle.get_odometry()
        if len(centroids) > 0:

            # get the centroid that is furthest left
            most_left_centroid = sorted(centroids, key=lambda x: x[0])[0]
            print(centroids)
            print(most_left_centroid)
            

            # measure the distance to the pipe from point cloud
            x1, y1, z1, dist1 = pc_to_distance(pc, int(most_left_centroid[1]), int(most_left_centroid[0]))
            x, y, current_angle = turtle.get_odometry()
        '''
        turtle.reset_odometry()
        turtle.wait_for_odometry()
        rotate_by_angle(turtle, "LEFT", math.radians(angle_range) - 0.01)

        #print(filtered.shape)
        print(filtered[int(MIDCOL)][int(MIDROW)])
        if filtered[int(MIDCOL)][int(MIDROW)] == 0.0:
            turtle.cmd_velocity(angular = -0.2)
            return
        
        x1, y1, z1, dist1 = pc_to_distance(pc, MIDROW, MIDCOL)
        x, y, current_angle = turtle.get_odometry()
        distance_and_angle.append([dist1*math.cos(current_angle), dist1*math.sin(current_angle)])
        state = LOSE_CENTER
        if current_angle > angle_range:
            state = CALCULATE
        

    if state == MOVE_TO_GATE:
        x, y, angle = turtle.get_odometry()
        print("x: ", x)
        print("end_distance:", end_distance)
        
        if x > end_distance:
            if target == 1:
                state = FACE_GATE
            elif target == 2:
                if next_gate_color == RED:
                    next_gate_color = BLUE
                elif next_gate_color == BLUE:
                    next_gate_color = RED
                else:
                    next_gate_color = RED
                    # next_gate_color = find_closest_gate_color(image)
                
                state = LOOKING_FOR_GATE

    if state == ROTATE_LEFT_TOWARD_GATE:
        x, y, angle = turtle.get_odometry()
        print("angle: ", angle)
        print("end_angle: ", end_angle)
        
        if (-1) * angle < end_angle:
            state = MOVE_TO_GATE
            turtle.reset_odometry()
            turtle.wait_for_odometry()

    if state == ROTATE_RIGHT_TOWARD_GATE:
        x, y, angle = turtle.get_odometry()
        print("angle: ", angle)
        print("end_angle: ", end_angle)
        
        if (-1) * angle > end_angle:
            state = MOVE_TO_GATE
            turtle.reset_odometry()
            turtle.wait_for_odometry()


    if state == CALCULATE:
        #print("len(centroids): ", len(centroids))
        #x1, y1, z1, dist1 = pc_to_distance(pc, int(centroids[0][1]), int(centroids[0][0]))
        #x2, y2, z2, dist2 = pc_to_distance(pc, int(centroids[1][1]), int(centroids[1][0]))
        print("state is CALCULATE. distance_and_angle: {}".format(distance_and_angle))
        state = FINISH
        #if x1 != math.nan and y1 != math.nan and z1 != math.nan and x2 != math.nan and y2 != math.nan and z2 != math.nan:
        '''
        if len(distance_and_angle) > 0:
            print("=============================")
            print("G1: {} [{}][{}] \nG2: {} [{}][{}]".format(dist1, x1, z1, dist2, x2, z2))
            angle1, dist, angle2 = get_directions(x1, z1, x2, z2, 0.2)
            print("angle1:\t", math.degrees(angle1), " deg")
            print("dist:\t", dist, " m")
            print("angle2:\t", math.degrees(angle2), " deg")
            print("=============================")

            if angle1 != math.nan and dist != math.nan:
                turtle.reset_odometry()
                turtle.wait_for_odometry()
                x, y, angle = turtle.get_odometry()

                end_angle = angle1
                end_angle2 = angle2
                end_distance = dist

                target = 1


                if end_angle < 0:
                    state = ROTATE_LEFT_TOWARD_GATE
                else:
                    state = ROTATE_RIGHT_TOWARD_GATE
                
                cv2.imshow(WINDOW, image)
                cv2.waitKey(0)
        '''
    if count == 2 and previous_state == LOOKING_FOR_GATE:
        print("Waiting to finish motion...")
        # state = MEASURE_DISTANCE_TO_GATE
        state = ROTATE_AND_MEASURE


    if state == FACE_GATE:
        end_angle = end_angle2
        end_distance = 0.25
        target = 2
        
        if end_angle < 0:
            state = ROTATE_LEFT_TOWARD_GATE
        else:
            state = ROTATE_RIGHT_TOWARD_GATE

    # if state == FACE_GATE:
    #     if count == 2:
    #         # If there are 2 pipes in the image
    #         # find the center point between the two pipes
    #         image, center_col, center_row = find_center(image, centroids)

    #         if abs(center_col - MIDCOL) < 30:
    #             # If we're close to the center move forward
    #             state = GO_THROUGH_GATE
    #         else:
    #             # If we're NOT close to the center rotate until we're close
    #             if center_col > MIDCOL:
    #                 state = ROTATE_RIGHT
    #             else:
    #                 state = ROTATE_LEFT
    #     else:
    #         state = ROTATE_LEFT
    
    # if state == ROTATE_LEFT or state == ROTATE_RIGHT:
    #     if count != 2:
    #         state == FACE_GATE

    # if state == GO_THROUGH_GATE and timeout <= 0:
    #     if next_gate_color == RED:
    #         next_gate_color = BLUE
    #     elif next_gate_color == BLUE:
    #         next_gate_color = RED
    #     else:
    #         next_gate_color = find_closest_gate_color(image)
        
    #     state = LOOKING_FOR_GATE

    print("\nFound {} {} objects".format(count, next_gate_color))
    # if center_row != 0 and center_col != 0:
    #     print("Center of gate:  [{}, {}]".format(center_row, center_col))
    #     print("Distance of gatecenter from center of the screen in px: {}".format(abs(MIDCOL - center_col)))
    print("Setting state from {} to {}".format(previous_state, state))
    print("-------------------------------")

    # show image
    cv2.imshow(WINDOW, image)
    cv2.waitKey(1)

    return state, next_gate_color, timeout


def main():
    print("Starting...")

    turtle.register_bumper_event_cb(bumper_callback)
    turtle.reset_odometry()

    cv2.namedWindow(WINDOW)

    # Default robot state is LOOKING_FOR_GATE
    state = LOOKING_FOR_GATE
    previous_state = LOOKING_FOR_GATE
    next_gate_color = RED
    timeout = 1000

    while not turtle.is_shutting_down() and isRunning and state != FINISH:
        # Look for any gate and update state
        #print("{}, {} = next_tick({}, {})".format(state, next_gate_color, state, next_gate_color))
        
        previous_state = state
        state, next_gate_color, timeout = next_tick(previous_state, next_gate_color, timeout)

        # Update velocity based on current state
        if motors_enabled:
            if state == LOOKING_FOR_GATE:
                turtle.cmd_velocity(angular = 0.2)
            if state == MEASURE_DISTANCE_TO_GATE:
                turtle.cmd_velocity(angular = 0)
                cv2.waitKey(2000)
            
            if state == ROTATE_LEFT:
                turtle.cmd_velocity(angular = 0.4)
            if state == ROTATE_RIGHT:
                turtle.cmd_velocity(angular = -0.4)
            if state == GO_THROUGH_GATE:
                turtle.cmd_velocity(linear = 0.1)

            if state == ROTATE_LEFT_TOWARD_GATE:
                turtle.cmd_velocity(angular = 0.2)
            if state == ROTATE_RIGHT_TOWARD_GATE:
                turtle.cmd_velocity(angular = -0.2)

            if state == MOVE_TO_GATE:
                turtle.cmd_velocity(linear = 0.1)


    # Play finish sound
    turtle.play_sound(1)

    # Stop moving before exiting program
    turtle.cmd_velocity(linear=0)
    turtle.cmd_velocity(angular=0)


if __name__ == "__main__":
    main()
