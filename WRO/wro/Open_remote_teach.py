from Uart_Disctance_Sensor import readout
from servo_control import move_servo
from motorcontrol import elore, hatra, stop
from time import sleep
import time

import sys
import select
import tty
import termios
import RPi.GPIO as GPIO

class Servo:
    def __init__(self, pin):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, 50)
        self.pwm.start(0)
        self.steering = 0
    
    def set_steering(self, steering):
        self.steering = min(max(steering, 0), 200)
        self.pwm.ChangeDutyCycle(2+(steering/18.))

    def get_steering(self):
        return self.steering




def billentyu_lenyomva():
    return bool(select.select([sys.stdin], [], [], 0)[0])

old_terminal_settings = termios.tcgetattr(sys.stdin)


# ---- Kormany skala ----
# egyenes = 100, teljesen balra = 200, teljesen jobbra = 0
move_servo(100)  # egyenes
elore()

# Ha egy szenzor idotullepest/ervenytelen valaszt ad, a readout() None-t ad
# vissza ahelyett, hogy crashelne. A szenzor 2-450cm (20-4500mm) kozt mer.
# Minden, ami ennel nagyobb (vagy None), egyarant "nincs semmi a kozelben,
# amennyire a szenzor latja" -- ezert mindket esetben ugyanarra a realis
# maximumra vagjuk le, kulonben egy hianyzo/hibas adat oriasi, irrealis
# kilenget okozhatna a kormany-formulaban.
MAX_RANGE = 4500
DEFAULT_DISTANCE = MAX_RANGE

servo = Servo(12)

def safe(value):
    if value is None:
        return DEFAULT_DISTANCE
    return min(value, MAX_RANGE)

# ---- Kormanyzasi parameterek (Open Challenge: csak fal-koveteses) ----
K_BASE = 3  # alap erzekenyseg egyenes szakaszon / enyhe elteresnel
K_BOOST = 10      # plusz erzekenyseg, amikor mar nagyon kozel a fal elol
FRONT_THRESH = 800   # ez alatt mar "sarok-kozelsegnek" szamit
steering = 100

readout_time = 0
n_readout = 0

servo_time = 0
n_servo = 0

try:
    tty.setcbreak(sys.stdin.fileno())
    with open('teaching.txt', 'wt') as f:
        while True:
            t0 = time.monotonic()
            Disctance_Data = readout()
            # verified sensor order: front, right, back, left
            Front = safe(Disctance_Data[0])
            Rside = safe(Disctance_Data[1])
            Back = safe(Disctance_Data[2])
            Lside = safe(Disctance_Data[3])
            t1 = time.monotonic()
            c = 'X'
            if billentyu_lenyomva():
                c = sys.stdin.read(1)
                print('Billentyu:', c, '\n\n')
                if c == '\x1b':
                    break
                if c.lower() == 'a':
                    print('\n steering +')
                    steering += 200
                elif c.lower() == 'd':
                    print('\n steering -')
                    steering -= 200
                elif c.lower() == 's':
                    print('\n steering =')
                    steering = 100
                elif c.lower() == 'q':

                    break
            steering = min(200, max(0, steering))
            t2 = time.monotonic()
            servo.set_steering(steering)
            t3 = time.monotonic()
            f.write(f'{Front}\t{Rside}\t{Back}\t{Lside}\t{steering}\t{c}\n')
            print(f'{Front=}\t{Rside=}\t{Back=}\t{Lside=}\t{steering=}\t{c=}\t{1000*(time.monotonic()-t0):.3f} ms               ',end='\r')
            readout_time += t1-t0
            servo_time += t3-t2
            n_readout += 1
            n_servo += 1
finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_terminal_settings)
    print('Servo: ', servo_time / n_servo)
    print('Readout: ', readout_time / n_readout)


