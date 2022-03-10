from robolab_turtlebot import Turtlebot, Rate, get_time
import math

turtle = Turtlebot()
# turtle = Turtlebot(rgb=True, depth=True, pc=True)
rate = Rate(10)

isRunning = True

# Names bumpers and events
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']

def goForward():
    turtle.cmd_velocity(linear = 0.1)

def forceStop():
    print('FORCE STOPPING')
    global isRunning
    isRunning = False
    turtle.cmd_velocity(linear = 0)
    turtle.cmd_velocity(angular = 0)
    quit()

def rotateLeft():
    turtle.cmd_velocity(angular = 0.4)

def rotateRight():
    turtle.cmd_velocity(angular = -0.4)

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

def drive1m():
    t = get_time()
    while not turtle.is_shutting_down() and isRunning and get_time() - t < 10:
        goForward()
        print(turtle.get_odometry())
        rate.sleep()

def rotate180():
    currentAngle = turtle.get_odometry()[2]
    while not turtle.is_shutting_down() and isRunning and currentAngle > -0.1 and  currentAngle <= math.pi :
        rotateLeft()
        print(turtle.get_odometry())
        rate.sleep()
        currentAngle = turtle.get_odometry()[2]

def main():
    print('Starting...')
    turtle.register_bumper_event_cb(bumper_cb)
    turtle.reset_odometry()

    while not turtle.is_shutting_down() and isRunning:
        drive1m()
        rotate180()
    
    turtle.cmd_velocity(linear = 0)


if __name__ == '__main__':
    main()
