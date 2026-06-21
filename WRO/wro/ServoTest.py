from servo_control import move_servo
from time import sleep

while True:
    move_servo(int(input()))
