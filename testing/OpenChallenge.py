import time
import RPi.GPIO as GPIO
import sys

GPIO.setmode(GPIO.BOARD)


def gomb_megnyomva():
    # 1 -> nincs lenyomva. 0 -> le van nyomva
    return GPIO.input(11) == 0


GPIO.setup(11, GPIO.IN)


class Servo:
    def __init__(self, pin):
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, 50)
        self.pwm.start(0)
        self.steering = 0

    def set_steering(self, steering):
        self.steering = min(max(steering, 0), 200)
        self.pwm.ChangeDutyCycle(2 + (steering / 18.0))

    def get_steering(self):
        return self.steering


# Megnyomtak a gombot, varunk 2 mp-et
from Uart_Disctance_Sensor import readout
from motorcontrol import elore, stop

time.sleep(1)

servo = Servo(12)
FORWARD = 85
servo.set_steering(FORWARD)
steer = 0
elore()
try:
    while not gomb_megnyomva():
        # verified sensor order: front, right, back, left
        Front, Rside, Back, Lside = readout()
        if Front < 1000:
            if Lside > Rside and Lside > 1000:
                servo.set_steering(200)
                time.sleep(2.35)
                steer += 1
                servo.set_steering(FORWARD)
            elif Rside > 1000:
                servo.set_steering(0)
                time.sleep(2.75)
                steer += 1
                servo.set_steering(FORWARD)
        if steer == 12:
            time.sleep(0.1)
            break
 
            
finally:
    stop()
