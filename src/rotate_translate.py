from robolab_turtlebot import Turtlebot, Rate, get_time


def rotate_by_angle(turtle, direction, end_angle):
    rate = Rate(10)
    if direction == "LEFT":
        vel = 0.5
    if direction == "RIGHT":
        vel = -0.5
    turtle.reset_odometry()
    turtle.wait_for_odometry()
    x, y, angle = turtle.get_odometry()
    while angle < end_angle:
        turtle.cmd_velocity(angular=vel)
        rate.sleep()
        x, y, angle = turtle.get_odometry()
    

def go_distance(turtle, end_distance, vel):
    rate = Rate(10)
    turtle.reset_odometry()
    turtle.wait_for_odometry()
    x, y, angle = turtle.get_odometry()
    while y < end_distance:
        turtle.cmd_velocity(linear=vel)
        rate.sleep()
        x, y, angle = turtle.get_odometry()
        print(x,y, angle)
