from __future__ import print_function

import sys

from robolab_turtlebot import Turtlebot

from scipy.misc import imsave

turtle = Turtlebot(rgb=True)
turtle.wait_for_rgb_image()
rgb = turtle.get_rgb_image()

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = 'capture_rgb.png'

print('Image saved as {}'.format(filename))
imsave(filename, rgb)
