import numpy as np
import cv2

x_range = (-0.3, 0.3)
z_range = (0.3, 3.0)

def get_pc_mask(pc):
    mask = pc[:, :, 1] > x_range[0]

    # mask point too far and close
    mask = np.logical_and(mask, pc[:, :, 2] > z_range[0])
    mask = np.logical_and(mask, pc[:, :, 2] < z_range[1])

    if np.count_nonzero(mask) <= 0:
        return None

    # empty image
    image = np.zeros(mask.shape)

    # assign depth i.e. distance to image
    image[mask] = np.int8(pc[:, :, 2][mask] / 3.0 * 255)
    im_color = cv2.applyColorMap(255 - image.astype(np.uint8), cv2.COLORMAP_JET)

    return im_color
    