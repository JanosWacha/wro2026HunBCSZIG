from GetThing import get_thing
from uart_test import readout
from servo_control import move_servo
from motorcontrol import elore, hatra, stop
import constants

steering = 0
Lside = 0
Rside = 0
Front = 0
elore()
while True:
    thing = get_thing()
    r = readout()
    Lside = r[constants.DISTANCEDETECTOR_LEFT]
    Rside = r[constants.DISTANCEDETECTOR_RIGHT]
    Front = r[constants.DISTANCEDETECTOR_FRONT]
    Back = r[constants.DISTANCEDETECTOR_BACK]
    if Lside <= 30 or Rside <= 30 or Front <= 20:
        hatra()
    else:
        elore()
    if thing == "Red":
        steering = -30
    elif thing == "Green":
        steering = 30
    elif Lside > 450 and steering == 0 and Rside > 450:
        steering = 0
    if Lside < 400 and thing == 0:
        steering = 20
    if Rside < 400 and thing == 0:
        steering = -20
    if Front < 400 and Rside < 850 and Lside > 850:
        steering = -45
        direction = "counterclockwise"
    elif Front < 400 and Lside < 850 and Rside > 850:
        steering = 45
        direction = "clockwise"
    move_servo(steering)
