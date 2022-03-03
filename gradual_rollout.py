from robolab_turtlebot import Turtlebot, Rate, get_time

turtle = Turtlebot()
rate = Rate(10)

isRunning = False

# Names bumpers and events
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']

def goForward():
    turtle.cmd_velocity(linear = 0.1)

def forceStop():
    print('FORCE STOPPING')
    sRunning = False
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

def main():
    turtle.register_bumper_event_cb(bumper_cb)
    turtle.reset_odometry()

    isRunning = True

    t = get_time()

    while not turtle.is_shutting_down():
        while get_time() - t < 10:
            goForward()
            # print(turtle.get_odometry())
            rate.sleep()


if __name__ == '__main__':
    main()