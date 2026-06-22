import RPi.GPIO as GPIO
import time

#Moves the servo to the given angle inside a function so we can import it in different files.
def move_servo(angle):
        #Set the GPIO mode and setup the servo pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(12,GPIO.OUT)
        servo1 = GPIO.PWM(12,50)
        #Start the PWM and set the duty cycle to move the servo to the desired angle.
        servo1.start(0)
        servo1.ChangeDutyCycle(2+(angle/18))
        time.sleep(0.0001)