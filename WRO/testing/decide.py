from GetThing import get_thing
from uart_test import readout
from servo_control import move_servo
from motorcontrol import elore, hatra, stop

steering = 0
Lside = 0
Rside = 0
Front = 0
elore()
while True: 
    thing = get_thing()
    Lside = readout()[1]
    Rside = readout()[2]
    Front = readout()[0]
    if Lside <= 10 or Rside <= 10 or Front <= 10:
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
    elif Front < 400 and Lside < 850 and Rside > 850:
        steering = 45
    move_servo(steering)
