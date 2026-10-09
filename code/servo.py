from RPi import GPIO
import time


class Servo:
        PWM_FREQ = 500 # Hz
        PULSE_WIDTH_LEFT = 0.0005 # sec
        PULSE_WIDTH_RIGHT = 0.0017 # sec
        STEERING_MIN = 20
        STEERING_MAX = 280
        LIMIT_MIN = 40
        LIMIT_MAX = 260

        def __init__(self, pin=18, log=True, pindec=True):
            self.log=log
            self.DC_LEFT = self.PULSE_WIDTH_LEFT * self.PWM_FREQ
            self.DC_RIGHT = self.PULSE_WIDTH_RIGHT * self.PWM_FREQ
            print(f'{self.DC_LEFT=}, {self.DC_RIGHT=}')
            if pindec:
                GPIO.setup(pin, GPIO.OUT)
            self.pwm = GPIO.PWM(pin, self.PWM_FREQ)
            self.pwm.start(0.5*(self.DC_LEFT + self.DC_RIGHT)*100)
            self.go_right()
            time.sleep(0.5)
            self.go_left()
            time.sleep(0.5)
            self.go_forward()

        def set_steering(self, steering):
            if self.log:
                print(f'Setting steering to {steering}')
            self.steering = min(max(steering, self.LIMIT_MIN), self.LIMIT_MAX)
            if self.log:
                print(f'Clipped steering: {self.steering}')
            dc = (self.DC_LEFT + 
                (self.steering - self.STEERING_MIN) / (self.STEERING_MAX - self.STEERING_MIN) * 
                (self.DC_RIGHT - self.DC_LEFT))
            if self.log:
                print(f'Setting dc to {dc*100}')
            self.pwm.ChangeDutyCycle(dc*100)

        def set_pulsewidth(self, pw):
            dc = pw * self.PWM_FREQ
            self.pwm.ChangeDutyCycle(dc*100)

        def get_steering(self):
            return self.steering

        def go_forward(self):
            self.set_steering((self.STEERING_MIN+self.STEERING_MAX)/2)

        def go_right(self):
            self.set_steering(self.STEERING_MIN)

        def go_left(self):
            self.set_steering(self.STEERING_MAX)


if __name__ == "__main__":
    try:
        GPIO.setmode(GPIO.BCM)
        s = Servo()
        while i := input("Írj be egy helyet 20 és 280 között. Ha nincs input, leáll:"):
            s.set_steering(int(i))
    finally:
        GPIO.cleanup()