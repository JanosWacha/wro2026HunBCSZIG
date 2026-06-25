import cv2
from picamera2 import Picamera2

import numpy as np
import time

#Picamera2 setup
cam = Picamera2()
#width, height = 3280, 2464
width, height = 640, 480
RED_THRESHOLD = 200
RED_MIN_PERCENT = 75

cam.configure(
    cam.create_preview_configuration(
        main={"format": 'XRGB8888', "size": (width, height)}, display=None))
cam.start()

#Colour ranges for red and green in HSV colour spacew
lower_red1 = np.array([0, 100, 100])
upper_red1 = np.array([10, 255, 255])

lower_red2 = np.array([160, 100, 100])
upper_red2 = np.array([180, 255, 255])

lower_green = np.array([35, 50, 50])
upper_green = np.array([85, 255, 255])

#The function that captures the image of the camera and checks if there is a a red or green obstacle on the image.
#Then it decides that it is red or green and returns it.
def get_thing():
    N_oszlop = 4
    N_sor = 4
    frame = cam.capture_array()
    height, width = frame.shape[:2]
    sormagassag = height // N_sor
    oszlopszelesseg = width // N_oszlop
    color = np.zeros((N_sor, N_oszlop))
    for i_oszlop in range(N_oszlop):
        for i_sor in range(N_sor):
            resz = frame[i_sor*sormagassag:(i_sor+1)*sormagassag, i_oszlop*oszlopszelesseg:(i_oszlop+1)*oszlopszelesseg, :]
            
            redmedian = np.median(resz[:, :, 2])
            greenmedian = np.median(resz[:, :, 1])
            bluemedian = np.median(resz[:, :, 0])
            
            # Zöld felismerése: zöld csatorna mediánja > kéké, zöld csatorna mediánja > pirosé, zöld csatorna mediánja > 100
            if redmedian < greenmedian and greenmedian > 100 and bluemedian < greenmedian:
                color[i_sor, i_oszlop] = 2
            # Piros felismerése: piros csatorna mediánja > 200, többié < 50
            if redmedian > 200 and greenmedian < 50 and bluemedian < 50:
                color[i_sor, i_oszlop] = 1

#    print('Piros:', np.sum(color==1), 'Zold:', np.sum(color==2))
#    print('Piros:', np.sum(color[:, :N_oszlop//2]==1), np.sum(color[:, N_oszlop//2:]==1))
#    print('Zold:', np.sum(color[:, :N_oszlop//2]==2), np.sum(color[:, N_oszlop//2:]==2))

    piros_van = (color[3*sormagassag:4*sormagassag] == 1).sum() > 1
    zold_van = (color[3*sormagassag:4*sormagassag] == 2).sum() > 1
    return piros_van, zold_van
    

if __name__ == '__main__':
    while True:
        p, z = get_thing()
        if p:
            print('Piros')
        if z: 
            print('Zold')
        time.sleep(1)
