from motorcontrol import elore, hatra, stop
from typing import Literal
from uart_test import readout
from servo_control import move_servo
import constants
from time import time, sleep

# Beni, ez akkor működik, ha ott vagyunk a parkoló előtt:

# irány   parkoló      fal
# |          |         |
# |          |         v
# -v----------v--------------
# <-      |         |
#   [autó]


def parking(direction: Literal["clockwise", "counterclockwise"]):
    hatra()
    if direction == "counterclockwise":
        t = time()
        while readout()[constants.DISTANCEDETECTOR_RIGHT] > 20:
            pass
        move_servo(45)
        while readout()[constants.DISTANCEDETECTOR_BACK] > 100:
            pass
        t2 = time()
        move_servo(-45)
        sleep(t2 - t)
        move_servo(0)
    else:
        t = time()
        while readout()[constants.DISTANCEDETECTOR_LEFT] > 20:
            pass
        move_servo(-45)
        while readout()[constants.DISTANCEDETECTOR_BACK] > 100:
            pass
        t2 = time()
        move_servo(45)
        sleep(t2 - t)
        move_servo(0)
