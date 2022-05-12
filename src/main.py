#!/usr/bin/env python

from robolab_turtlebot import Turtlebot
import cv2

from distance import *
from constants import *
from partitioning import *
from angle_dist_angle import *
from show_depth import *
from transform_coords import *

isRunning = False
turtle = Turtlebot(rgb = True, pc = True)


def bumper_callback(msg):
    bumper_name = BUMPER_NAMES[msg.bumper]  # msg.bumper stores the id of bumper 0:LEFT, 1:CENTER, 2:RIGHT
    bumper_state = BUMPER_STATES[msg.state]  # msg.state stores the event 0:RELEASED, 1:PRESSED

    print("{} bumper {}".format(bumper_name, bumper_state))
    if bumper_state == "PRESSED":
        print("Bumber pressed. STOPPING...")
        global isRunning
        isRunning = False
        turtle.cmd_velocity(linear = 0)
        turtle.cmd_velocity(angular = 0)
        quit()

def button_callback(event):
    button_number = event.button  # event.button stores the id of button 0, 1 or 2
    button_state = BUTTON_STATES[event.state]  # event.state stores the event 0:RELEASED, 1:PRESSED
    
    if button_state == "PRESSED":
        print("Button {} pressed. Starting program...", button_number)
        global isRunning
        isRunning = True


def get_objects_from_rgb_image(next_gate_color, min_size):
    while True:
        image = turtle.get_rgb_image()
        if not image is None:
            break

    image, filtered, count, centroids = get_objects_for_color(image, next_gate_color, min_size)
    
    return image, filtered, count, centroids


def get_pc_image(count, centroids):
    while True:
        pc = turtle.get_point_cloud()
        if pc is None:
            continue

        pc_image = get_pc_mask(pc)
        if not pc_image is None:
            break

    pc_image = draw_crosshairs_for_color(pc_image, count, centroids, "black")
   
    return pc, pc_image


# ////////////////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////////////////////////////////////////////////////////////

def update_image(next_gate_color, min_size):
    image, filtered, count, centroids = get_objects_from_rgb_image(next_gate_color, min_size)
    pc, pc_image = get_pc_image(count, centroids)
    
    return image , filtered, count, centroids, pc, pc_image

def is_pipe_unique(pillars, xt, yt):
    EPSILON = 0.1
    print("Checking uniqueness of a new pipe at [{}][{}]".format(xt, yt))
    for i in range(0, len(pillars)):
        if abs(xt - pillars[i][0]) < EPSILON and abs(yt - pillars[i][1]) < EPSILON:
            return False
        
    print("its unique")
    return True

def detect_pipes_in_image(next_gate_color, next_state, count, pc, centroids, pillars, lookout_angle):
    print("detecting pipes in the image. Count = {}".format(count))
    for i in range(0, count):
        x, _, z, dist = pc_to_distance(pc, int(centroids[i][1]), int(centroids[i][0]))
        xt, zt = transform_coords(x, z, lookout_angle)
        print(f'>>>>> Found new pipe: xt: {xt}, zt: {zt}')
        if is_pipe_unique(pillars, xt, zt):
            pillars.append([xt, zt, dist])

    return next_state, pillars
    

def rotate_by_angle(target_angle, current_state, next_state):
    speed = 0.4 if target_angle > 0 else -0.4
    turtle.cmd_velocity(angular = speed)

    _, _, angle = turtle.get_odometry()
    print(f'Rotate by angle: current:{angle} --> target: {target_angle}')

    if abs(angle) > abs(target_angle):
        print(f'Finished rotation! Reseting odometry')
        turtle.cmd_velocity(angular = 0)
        turtle.reset_odometry()
        turtle.wait_for_odometry()
        return next_state

    return current_state
    

def measure_distance_to_gate(pillars):
    print(f'--------------------------------------')
    print(f'MEASURE DISTANCE TO GATE')

    if len(pillars) < 2:
        print("Unable to find gate")
        return INCREASE_LOOKOUT_ANGLE, None, None, None
    else:
        print("Ha! Found a gate")

        pillars = sorted(pillars, key=lambda x: x[2])

        x1 = pillars[0][0]
        z1 = pillars[0][1]
        x2 = pillars[1][0]
        z2 = pillars[1][1]
        dist1 = pillars[0][2]
        dist2 = pillars[1][2]
        print(f'x1: {x1}, z1: {z1}, x2: {x2}, z2: {z2}')
        pillars = []
        if (x1 != math.nan and z1 != math.nan and x2 != math.nan and z2 != math.nan):

            # GET DIRECTIONS
            angle1, dist, angle2 = get_directions(x1, z1, x2, z2, 0.2)

            if angle1 != math.nan and dist != math.nan and angle2 != math.nan:

                print("=============================")
                print(f'G1: {dist1} [{x1}][{z1}] \nG2: {dist2} [{x2}][{z2}]')
                print(f'angle1:\t{math.degrees(angle1)} deg')
                print(f'dist:\t {dist} m')
                print(f'angle2:\t{math.degrees(angle2)} deg')
                print("=============================")


                # cv2.waitKey(0)

                if angle1 != math.nan and dist != math.nan:
                    turtle.reset_odometry()
                    turtle.wait_for_odometry()
                    return ROTATE_TOWARD_GATE, angle1, dist, angle2
    
    return MEASURE_DISTANCE_TO_GATE, None, None, None


def drive(dist, current_state, next_state):
    direction = 1 if dist > 0 else -1
    turtle.cmd_velocity(linear = direction * 0.1)

    x, _, _ = turtle.get_odometry()
    print(f'dRIVE: current:{x} --> target: {dist}')

    if abs(x) > abs(dist):
        print(f'Finished drive!')
        turtle.cmd_velocity(linear = 0)
        return next_state

    return current_state


def detect_next_gate_color(current_gate_color, image, pc, min_size):
    if current_gate_color == RED:
        return DETECT_PIPES_IN_IMAGE, BLUE
    elif current_gate_color == BLUE:
        return DETECT_PIPES_IN_IMAGE, RED
    else:
        return DETECT_PIPES_IN_IMAGE, find_closest_gate_color(image, pc, min_size)


def main():
    print("Starting...")

    turtle.register_bumper_event_cb(bumper_callback)
    turtle.register_button_event_cb(button_callback)
    turtle.reset_odometry()

    cv2.namedWindow(WINDOW)
    cv2.namedWindow("PC")

    state = WAIT_FOR_BUTTON   # Starting state
    print("Push any button ON THE ROBOT to start the program")

    # Wait for the user to push a button on the robot to start the program
    while isRunning == False:
        cv2.waitKey(100)
        pass

    state = DETECT_PIPES_IN_IMAGE
    next_gate_color = GREEN     # First gate is always GREEN

    pillars = []
    LOOKOUT_ANGLE = 35
    min_size = 2000
    while not turtle.is_shutting_down() and isRunning:
        previous_state = state

        if state == DETECT_PIPES_IN_IMAGE or state == DETECT_PIPES_IN_IMAGE_LEFT or state == DETECT_PIPES_IN_IMAGE_RIGHT or state == MEASURE_DISTANCE_TO_GATE or state == DETECT_NEXT_GATE_COLOR:
            cv2.waitKey(1000)
        
            image , filtered, count, centroids, pc, pc_image = update_image(next_gate_color, min_size)
            cv2.imshow("PC", pc_image)
            cv2.imshow(WINDOW, image)
            cv2.imshow("mask", filtered)

        
        if state == DETECT_PIPES_IN_IMAGE:
            cv2.waitKey(500)
            state, pillars = detect_pipes_in_image(next_gate_color, LOOK_LEFT, count, pc, centroids, pillars, 0)
        elif state == LOOK_LEFT:
            state = rotate_by_angle(math.radians(LOOKOUT_ANGLE), LOOK_LEFT, DETECT_PIPES_IN_IMAGE_LEFT)
        elif state == DETECT_PIPES_IN_IMAGE_LEFT:    
            state,pillars = detect_pipes_in_image(next_gate_color, LOOK_RIGHT, count, pc, centroids, pillars, LOOKOUT_ANGLE)
        elif state == LOOK_RIGHT:                     
            state = rotate_by_angle(math.radians(-2 * LOOKOUT_ANGLE), LOOK_RIGHT, DETECT_PIPES_IN_IMAGE_RIGHT)
        elif state == DETECT_PIPES_IN_IMAGE_RIGHT:    
            state, pillars = detect_pipes_in_image(next_gate_color, LOOK_BACK_TO_CENTER, count, pc, centroids, pillars, -LOOKOUT_ANGLE)
        elif state == LOOK_BACK_TO_CENTER:            
            state = rotate_by_angle(math.radians(LOOKOUT_ANGLE), LOOK_BACK_TO_CENTER, MEASURE_DISTANCE_TO_GATE)


        elif state == MEASURE_DISTANCE_TO_GATE:       
            state, angle1, dist, angle2 = measure_distance_to_gate(pillars)
        elif state == INCREASE_LOOKOUT_ANGLE:                     
            pillars = []
            LOOKOUT_ANGLE = 65
            state = DETECT_PIPES_IN_IMAGE


        elif state == ROTATE_TOWARD_GATE:             
            state = rotate_by_angle(-angle1, ROTATE_TOWARD_GATE, DRIVE_TOWARD_GATE)
        elif state == DRIVE_TOWARD_GATE:             
            state = drive(dist, DRIVE_TOWARD_GATE, ROTATE_TO_FACE_GATE)
        elif state == ROTATE_TO_FACE_GATE:            
            state = rotate_by_angle(-angle2, ROTATE_TO_FACE_GATE, DRIVE_THROUGH_GATE)
        elif state == DRIVE_THROUGH_GATE:             
            state = drive(0.30, DRIVE_THROUGH_GATE, DETECT_NEXT_GATE_COLOR)
        elif state == DETECT_NEXT_GATE_COLOR:         
            state, next_gate_color = detect_next_gate_color(next_gate_color, image, pc, min_size)
            pillars = []
            LOOKOUT_ANGLE = 35
            min_size = 3200

        print(f'Pillars: {pillars}')

        print(f'\nFound {count} {next_gate_color} objects')
        print(f'Setting state from {previous_state} to {state}')
        print("-------------------------------")


    # Play finish sound
    turtle.play_sound(1)

    # Stop moving before exiting program
    turtle.cmd_velocity(linear = 0)
    turtle.cmd_velocity(angular = 0)


if __name__ == "__main__":
    main()
