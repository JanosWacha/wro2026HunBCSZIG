from gpiozero import Button
from RPi import GPIO

class Servo:
    def __init__(self, pin=12):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, 50)
        self.pwm.start(0)
        self.steering = 0

class OpenChallenge:
    def __init__(self):
        self.cnt = 0
        self.wait_for_button_press()
    
    def wait_for_button_press(self):
        pause = True
        b = Button(17)
        def fgv():
            b.close()
            nonlocal pause
            pause = False
        b.when_pressed = fgv
        while pause:
            pass
    