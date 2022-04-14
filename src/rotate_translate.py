from robolab_turtlebot import Turtlebot, Rate, get_time


def rotate_by_angle(turtle, direction, end_angle):
    rate = Rate(10)
    if direction == "LEFT":
        vel = 0.1
    if direction == "RIGHT":
        vel = -0.1
    turtle.reset_odometry()
    turtle.wait_for_odometry()
    x, y, angle = turtle.get_odometry()
    while angle < end_angle:
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
