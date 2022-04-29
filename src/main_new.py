#!/usr/bin/env python

from robolab_turtlebot import Turtlebot
import cv2

from distance import *
from constants import *
from partitioning import *
from rotate_translate import *
from angle_dist_angle import *
from show_depth import *

isRunning = True
turtle = Turtlebot(rgb=True, pc=True)

motors_enabled = True


def bumper_callback(msg):
    bumper_name = BUMPER_NAMES[
        msg.bumper
    ]  # msg.bumper stores the id of bumper 0:LEFT, 1:CENTER, 2:RIGHT
    bumper_state = BUMPER_STATES[
        msg.state
    ]  # msg.state stores the event 0:RELEASED, 1:PRESSED

    print("{} bumper {}".format(bumper_name, bumper_state))
    if bumper_state == "PRESSED":
        print("Bumber pressed. STOPPING...")
        global isRunning
        isRunning = False
        turtle.cmd_velocity(linear=0)
        turtle.cmd_velocity(angular=0)
        quit()


def get_objects_from_rgb_image(next_gate_color):
    image = turtle.get_rgb_image()
    if image is None:
        raise Exception("No RGB Image received")

    image, filtered, count, centroids = get_objects_for_color(image, next_gate_color)
    cv2.imshow(WINDOW, image)
    cv2.imshow("mask", filtered)

    return image, filtered, count, centroids


def get_pc_image(count, centroids):
    pc = turtle.get_point_cloud()
    if pc is None:
        raise Exception("No PointCloud received")

    pc_image = return_mask(pc)
    pc_image = draw_crosshairs_for_color(pc_image, count, centroids, "hh")
    cv2.imshow("PC", pc_image)

    return pc, pc_image


# ////////////////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////////////////////////////////////////////////////////////

def detect_pipes_in_image(next_gate_color, next_state):
    image, filtered, count, centroids = get_objects_from_rgb_image(next_gate_color)
    pc, pc_image = get_pc_image(count, centroids)

    new_pillars = []
    if count > 0:
        x1, _, z1, _ = pc_to_distance(pc, int(centroids[0][1]), int(centroids[0][0]))
        new_pillars.append([x1, z1])

    return next_state, image , filtered, count, centroids, pc, pc_image, new_pillars


def rotate_by_angle(target_angle, current_state, next_state):
    _, _, angle = turtle.get_odometry()
    direction = 1 if target_angle > 0 else -1

    if abs(angle) > abs(target_angle):
        turtle.cmd_velocity(angular = direction * 0.2)
        turtle.reset_odometry()
        turtle.wait_for_odometry()
        return next_state

    return current_state


def look_back_to_center():
    turtle.cmd_velocity(angular = 0.2)
    _, _, angle = turtle.get_odometry()
    if angle > 0:
        turtle.reset_odometry()
        turtle.wait_for_odometry()
        return MEASURE_DISTANCE_TO_GATE

    return LOOK_BACK_TO_CENTER
    

def measure_distance_to_gate(pillars):
    if len(pillars) < 2:
        print("Unable to find gate")
        return DRIVE_BACK
    else:
        print("Ha! Found a gate")
        print(f'Pillars: {pillars}')
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

            print("=============================")
            print(f'G1: {dist1} [{x1}][{z1}] \nG2: {dist2} [{x2}][{z2}]')
            print(f'angle1:\t{math.degrees(angle1)} deg')
            print(f'dist:\t {dist} m')
            print(f'angle2:\t{math.degrees(angle2)} deg')
            print("=============================")

            if angle1 != math.nan and dist != math.nan:
                turtle.reset_odometry()
                turtle.wait_for_odometry()
                return ROTATE_TOWARD_GATE, angle1, dist, angle2

    return MEASURE_DISTANCE_TO_GATE


def drive(dist, current_state, next_state):
    direction = 1 if dist > 0 else -1
    turtle.cmd_velocity(linear = direction * 0.1)

    x, _, _ = turtle.get_odometry()
    if abs(x) > abs(dist):
        return next_state

    return current_state


def detect_next_gate_color(current_gate_color, image):
    if current_gate_color == RED:
        return DETECT_PIPES_IN_IMAGE, BLUE
    elif current_gate_color == BLUE:
        return DETECT_PIPES_IN_IMAGE, RED
    else:
        return DETECT_PIPES_IN_IMAGE, find_closest_gate_color(image)


def main():
    print("Starting...")

    turtle.register_bumper_event_cb(bumper_callback)
    turtle.reset_odometry()

    cv2.namedWindow(WINDOW)
    cv2.namedWindow("PC")

    state = DETECT_PIPES_IN_IMAGE
    next_gate_color = GREEN

    pillars = []
    while not turtle.is_shutting_down() and isRunning and state != FINISH:
        previous_state = state
        LOOKOUT_ANGLE = 25

        if state == DETECT_PIPES_IN_IMAGE: state, image , filtered, count, centroids, pc, pc_image, new_pillars = detect_pipes_in_image(next_gate_color, LOOK_LEFT)
        if state == LOOK_LEFT: state = rotate_by_angle(math.radians(LOOKOUT_ANGLE), LOOK_LEFT, DETECT_PIPES_IN_IMAGE_LEFT)
        if state == DETECT_PIPES_IN_IMAGE_LEFT: state = detect_pipes_in_image(next_gate_color, LOOK_RIGHT)
        if state == LOOK_RIGHT: state = rotate_by_angle(math.radians(-2 * LOOKOUT_ANGLE), LOOK_RIGHT, LOOK_BACK_TO_CENTER)
        if state == DETECT_PIPES_IN_IMAGE_RIGHT: state = detect_pipes_in_image(next_gate_color, LOOK_BACK_TO_CENTER)
        if state == LOOK_BACK_TO_CENTER: state = look_back_to_center()

        if state == MEASURE_DISTANCE_TO_GATE: state, angle1, dist, angle2 = measure_distance_to_gate(pillars)
        if state == DRIVE_BACK: state = drive(-0.5, DRIVE_BACK, DETECT_PIPES_IN_IMAGE)

        if state == ROTATE_TOWARD_GATE: state = rotate_by_angle(angle1, ROTATE_TOWARD_GATE, DRIVE_TOWARDS_GATE)
        if state == DRIVE_TOWARDS_GATE: state = drive(dist, DRIVE_TOWARDS_GATE, ROTATE_TO_FACE_GATE)
        if state == ROTATE_TO_FACE_GATE: state = rotate_by_angle(angle2, ROTATE_TO_FACE_GATE, DRIVE_THROUGH_GATE)
        if state == DRIVE_THROUGH_GATE: state = drive(dist, DRIVE_THROUGH_GATE, DETECT_NEXT_GATE_COLOR)
        if state == DETECT_NEXT_GATE_COLOR: state, next_gate_color = detect_next_gate_color(next_gate_color, image)

        # Add newly found pillars
        pillars.append(new_pillars)

        print(f'\nFound {count} {next_gate_color} objects')
        print(f'Setting state from {previous_state} to {state}')
        print("-------------------------------")

    # Play finish sound
    turtle.play_sound(1)

    # Stop moving before exiting program
    turtle.cmd_velocity(linear=0)
    turtle.cmd_velocity(angular=0)


if __name__ == "__main__":
    main()
