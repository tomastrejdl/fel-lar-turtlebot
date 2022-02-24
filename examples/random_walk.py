#!/usr/bin/env python

from __future__ import print_function

import cv2

import numpy as np

from robolab_turtlebot import Turtlebot

MOVE = 1
ROTATE = 2

linear_vel = 0.2
angular_vel = 0.3

WINDOW = 'obstacles'

running = True
active = True


def click(vent, x, y, flags, param):
    global active
    active = not active
    print(active)


def main():

    turtle = Turtlebot(pc=True)

    print('Waiting for point cloud ...')
    turtle.wait_for_point_cloud()
    direction = None
    print('First point cloud recieved ...')

    cv2.namedWindow(WINDOW)
    cv2.setMouseCallback(WINDOW, click)

    while not turtle.is_shutting_down():
        # get point cloud
        pc = turtle.get_point_cloud()

        if pc is None:
            print('No point cloud')
            continue

        # mask out floor points
        mask = pc[:, :, 1] < 0.2

        # mask point too far
        mask = np.logical_and(mask, pc[:, :, 2] < 3.0)

        #if np.count_nonzero(mask) <= 0:
        #    print('All point are too far ...')
        #    continue

        # empty image
        image = np.zeros(mask.shape)

        # assign depth i.e. distance to image
        image[mask] = np.int8(pc[:, :, 2][mask] / 3.0 * 255)
        im_color = cv2.applyColorMap(255 - image.astype(np.uint8),
                                     cv2.COLORMAP_JET)

        # show image
        cv2.imshow(WINDOW, im_color)
        cv2.waitKey(1)

        # check obstacle
        mask = np.logical_and(mask, pc[:, :, 1] > -0.2)
        data = np.sort(pc[:, :, 2][mask])

        state = MOVE
        if data.size > 50:
            dist = np.percentile(data, 10)
            if dist < 0.6:
                state = ROTATE

        # command velocity
        if active and state == MOVE:
            turtle.cmd_velocity(linear=linear_vel)
            direction = None

        # ebstacle based rotation
        elif active and state == ROTATE:
            if direction is None:
                direction = np.sign(np.random.rand() - 0.5)
            turtle.cmd_velocity(angular=direction*angular_vel)


if __name__ == '__main__':
    main()
