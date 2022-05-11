from robolab_turtlebot import Turtlebot, Rate, get_time
import math
import numpy as np

def rotate_by_angle(turtle, direction, end_angle):
    rate = Rate(10)
    if direction == "LEFT":
        vel = 0.3
    if direction == "RIGHT":
        vel = -0.3
    turtle.reset_odometry()
    turtle.wait_for_odometry()
    x, y, angle = turtle.get_odometry()
    while abs(angle) < abs(end_angle):
        # print("angle: ", angle, ", end_angle: ", end_angle)
        turtle.cmd_velocity(angular=vel)
        x, y, angle = turtle.get_odometry()
        rate.sleep()
    
    print("Finished rotating")
    turtle.cmd_velocity(angular=0)
    

def go_distance(turtle, end_distance, vel):
    rate = Rate(10)
    turtle.reset_odometry()
    turtle.wait_for_odometry()
    x, y, angle = turtle.get_odometry()
    while y < end_distance:
        turtle.cmd_velocity(linear=vel)
        x, y, angle = turtle.get_odometry()
        rate.sleep()
        # print(x,y, angle)

    print("Finished going distance")
    turtle.cmd_velocity(linear=0)
