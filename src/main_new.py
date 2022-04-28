#!/usr/bin/env python

from robolab_turtlebot import Turtlebot
import numpy as np
import cv2

from distance import *
from constants import *
from partitioning import *
from rotate_translate import *
from angle_dist_angle import *
from show_depth import *

end_angle = 0
end_angle2 = 0
end_distance = 0
target = 1
SECOND_GATE_STATE = 0
pillars = []

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
    if pc is None:
      return

    
    # wait for image to be ready
    if image is None: return

    MIDROW = image.shape[0]/2
    MIDCOL = image.shape[1]/2
    pc_image = return_mask(pc)
    image, filtered, count, centroids = get_objects_for_color(image, next_gate_color)
    pc_image = draw_crosshairs_for_color(pc_image, count, centroids, "hh")
    cv2.imshow("mask", filtered)
    print(count)
    global end_angle
    global end_angle2
    global end_distance
    global target
    global SECOND_GATE_STATE
    global pillars

    center_row = center_col = 0
    
    if state == LOOK_FOR_SECOND_GATE:
      lookout_angle = 25
      if count > 0:
        x1, y1, z1, dist1 = pc_to_distance(pc, int(centroids[0][1]), int(centroids[0][0]))
        pillars.append([x1,z1])
        print(pillars)
      if count == 8:
        print("Was I supposed to find this?")
        state = MEASURE_DISTANCE_TO_GATE
      else:
        end_angle = math.radians(lookout_angle)
        end_angle2 = math.radians(-2*lookout_angle)
        if SECOND_GATE_STATE == 0: # ROTATE LEFT

          print("ROTATE LEFT")
          x, y, angle = turtle.get_odometry()
          if angle > end_angle:
            turtle.reset_odometry()
            turtle.wait_for_odometry()
            SECOND_GATE_STATE = 1
            
        if SECOND_GATE_STATE == 1: # TAKE A PICTURE
          print("TAKE A PICTURE")
          if count > 0:
            x1, y1, z1, dist1 = pc_to_distance(pc, int(centroids[0][1]), int(centroids[0][0]))
            pillars.append([x1,z1])
            print(pillars)
          SECOND_GATE_STATE = 2
          
        if SECOND_GATE_STATE == 2: # ROTATE RIGHT
          print("ROTATE RIGHT")
          x, y, angle = turtle.get_odometry()
          if angle < end_angle2:
            turtle.reset_odometry()
            turtle.wait_for_odometry()
            SECOND_GATE_STATE = 3
            
        if SECOND_GATE_STATE == 3: # TAKE A SECOND PICTURE
          print("TAKE A SECOND PICTURE")
          if count > 0:
            x1, y1, z1, dist1 = pc_to_distance(pc, int(centroids[0][1]), int(centroids[0][0]))
            pillars.append([x1,z1])
            print(pillars)
          SECOND_GATE_STATE = 4
          
        
        if SECOND_GATE_STATE == 4: # ROTATE LEFT
          print("ROTATE LEFT")
          x, y, angle = turtle.get_odometry()
          if angle > end_angle:
            turtle.reset_odometry()
            turtle.wait_for_odometry()
            SECOND_GATE_STATE = 5 
        
        if SECOND_GATE_STATE == 5: #Go or repeat
          if len(pillars) < 2:
            print("Unable to find second gate")
            print(pillars)
            SECOND_GATE_STATE = 0
          else:
            print("Ha! Found it anyway")
            print(pillars)
            x1 = pillars[0][0]
            z1 = pillars[0][1]
            x2 = pillars[1][0]
            z2 = pillars[1][1]
            print (x1,z1,x2,z2)
            pillars = []
            if x1 != math.nan and z1 != math.nan and x2 != math.nan and z2 != math.nan:
              print("=============================")
              print("G1: [{}][{}] \nG2: [{}][{}]".format(x1, z1, x2, z2))
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
                
                state = LOOK_FOR_SECOND_GATE # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!LOOKING_FOR_GATE 

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


    if state == MEASURE_DISTANCE_TO_GATE:
        print("len(centroids): ", len(centroids))
        if len(centroids) == 2:
          x1, y1, z1, dist1 = pc_to_distance(pc, int(centroids[0][1]), int(centroids[0][0]))
          x2, y2, z2, dist2 = pc_to_distance(pc, int(centroids[1][1]), int(centroids[1][0]))
          print(x1, z1, x2, z2)
          if x1 != math.nan and y1 != math.nan and z1 != math.nan and x2 != math.nan and y2 != math.nan and z2 != math.nan:
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

    if count == 2 and (previous_state == LOOKING_FOR_GATE):
        print("Waiting to finish motion...")
        state = MEASURE_DISTANCE_TO_GATE


    if state == FACE_GATE:
        end_angle = end_angle2
        end_distance = 0.35
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
    cv2.imshow("PC", pc_image)
    cv2.waitKey(1)

    return state, next_gate_color, timeout


def main():
    print("Starting...")

    turtle.register_bumper_event_cb(bumper_callback)
    turtle.reset_odometry()

    cv2.namedWindow(WINDOW)
    cv2.namedWindow("PC")

    # Default robot state is LOOKING_FOR_GATE
    state = LOOKING_FOR_GATE
    previous_state = LOOKING_FOR_GATE
    next_gate_color = GREEN
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
                
            if state == LOOK_FOR_SECOND_GATE:
              if SECOND_GATE_STATE == 0:
                turtle.cmd_velocity(angular = 0.2)
              if SECOND_GATE_STATE == 1:
                turtle.cmd_velocity(angular = 0)
                cv2.waitKey(2000)
              if SECOND_GATE_STATE == 2:
                turtle.cmd_velocity(angular = -0.2)
              if SECOND_GATE_STATE == 3:
                turtle.cmd_velocity(angular = 0)
                cv2.waitKey(2000)
              if SECOND_GATE_STATE == 4:
                turtle.cmd_velocity(angular = 0.2)
              if SECOND_GATE_STATE == 5:
                turtle.cmd_velocity(angular = 0)
                cv2.waitKey(1000)
              
                

    # Play finish sound
    turtle.play_sound(1)

    # Stop moving before exiting program
    turtle.cmd_velocity(linear=0)
    turtle.cmd_velocity(angular=0)


if __name__ == "__main__":
    main()
