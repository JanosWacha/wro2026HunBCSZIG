# Import libraries
import RPi.GPIO as GPIO
import time

# Set GPIO numbering mode


# Loop to allow user to set servo angle. Try/finally allows exit
# with execution of servo.stop and GPIO cleanup :)
def move_servo(angle):
        GPIO.setmode(GPIO.BOARD)
        angle = 90+angle

        # Set pin 11 as an output, and define as servo1 as PWM pin
        GPIO.setup(12,GPIO.OUT)
        servo1 = GPIO.PWM(12,50) # pin 11 for servo1, pulse 50Hz

        # Start PWM running, with value of 0 (pulse off)
        servo1.start(0)

        #Ask user for angle and turn servo to it
        servo1.ChangeDutyCycle(2+(angle/18))
        time.sleep(0.5)
        servo1.ChangeDutyCycle(0)


        servo1.stop()
        GPIO.cleanup()
if __name__ == "__main__":
        while i:=input() != "q":
                move_servo(int(i))

