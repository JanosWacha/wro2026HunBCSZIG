from RPi import GPIO

class Motor:
    def __init__(self, fwpin=20, bwpin=21, speed=100):
        GPIO.setup(fwpin, GPIO.OUT)
        GPIO.setup(bwpin, GPIO.OUT)
        self.e = GPIO.PWM(fwpin, 100)
        self.h = GPIO.PWM(bwpin, 100)
        self.speed = speed
        self.e.start(0)
        self.h.start(0)
    def elore(self):
        print("Előre")
        self.h.ChangeDutyCycle(0)
        self.e.ChangeDutyCycle(self.speed)
    def hatra(self):
        print("Hátra")
        self.e.ChangeDutyCycle(0)
        self.h.ChangeDutyCycle(self.speed)
    def stop(self):
        print("Stop")
        self.e.ChangeDutyCycle(0)
        self.h.ChangeDutyCycle(0)
    def demo(self):
        while (i:=input("Előre/Hátra/Stop/Kilép[e/h/s/q]").strip().lower()) != "q":
            if i == "e":
                self.elore()
            elif i == "h":
                self.hatra()
            else:
                self.stop()
        self.stop()
#Debug.
if __name__ == "__main__":
    try:
        GPIO.setmode(GPIO.BCM)
        m = Motor()
        m.demo()
    finally:
        GPIO.cleanup()
