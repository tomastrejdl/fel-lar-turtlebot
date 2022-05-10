import math

def transform_coords(x, y, rotation_angle_in_deg):
    distance = math.sqrt(x**2 + y**2)
    pole_angle = math.radians(rotation_angle_in_deg) - math.atan2(x, y)
    if pole_angle != 0:
        real_x_coords = (-(pole_angle / abs(pole_angle)) * distance * math.sin(abs(pole_angle)))
    else:
        real_x_coords = 0
    real_y_coords = distance * math.cos(abs(pole_angle))
    return real_x_coords, real_y_coords
