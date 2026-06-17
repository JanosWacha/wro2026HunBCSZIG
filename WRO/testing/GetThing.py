import cv2
from picamera2 import Picamera2

import numpy as np

cam = Picamera2()
width, height = 640, 480


cam.configure(
    cam.create_video_configuration(
        main={"format": 'XRGB8888', "size": (width, height)}))
cam.start()


lower_red1 = np.array([0, 100, 100])
upper_red1 = np.array([10, 255, 255])

lower_red2 = np.array([160, 100, 100])
upper_red2 = np.array([180, 255, 255])

lower_green = np.array([35, 50, 50])
upper_green = np.array([85, 255, 255])


def get_thing():
    frame = cam.capture_array()
    height, width = frame.shape[:2]
    savszel = width // 4
    sav1 = [0, savszel]
    sav2 = [savszel, savszel*2]
    sav3 = [savszel*2, savszel*3]
    sav4 = [savszel*3, width]

    G_sav = frame[:, savszel:savszel*3]

    hsv = cv2.cvtColor(G_sav, cv2.COLOR_BGR2HSV)

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask3 = cv2.inRange(hsv, lower_green, upper_green)

    RedInMask = cv2.countNonZero(mask1) + cv2.countNonZero(mask2)
    GreenInMask = cv2.countNonZero(mask3)
    if RedInMask > 4000 or GreenInMask > 4000:
        if RedInMask > GreenInMask:
            return "Red"
        else:
            return "Green"
    elif RedInMask < 4000 and GreenInMask < 4000:
        return 0


print(get_thing())
