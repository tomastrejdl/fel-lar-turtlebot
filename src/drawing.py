import cv2

from constants import RED, GREEN, BLUE 

def get_normalized_bgr(b, g, r):
    norm_r = r / (r + g + b)
    norm_g = g / (r + g + b)
    norm_b = b / (r + g + b)
    return norm_b, norm_g, norm_r

def draw_crosshair(image, crosshair_row, crosshair_col, R, G, B):
    for row in range(0, image.shape[0]):
        for col in range(0, image.shape[1]):
            if abs(row - crosshair_row) < 1 or abs(col - crosshair_col) < 1:
                image[row][col][0] = B
                image[row][col][1] = G
                image[row][col][2] = R
    return image

def draw_crosshairs_for_color(image, count, centroids, color):
    r = g = b = 0
    if color == RED: r = 255
    if color == GREEN: g = 255
    if color == BLUE: b = 255

    for i in range(0, count):
        image = draw_crosshair(image, int(centroids[i][1]), int(centroids[i][0]), r, g, b)

    return image

def draw_center(image, row, col):
    return cv2.circle(image, (row, col), 5, (255, 255, 255), -1)