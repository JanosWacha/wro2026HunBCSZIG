from GetThing import get_thing
from Uart_Disctance_Sensor import readout
from motorcontrol import elore, hatra, stop
from time import sleep
import time
import RPi.GPIO as GPIO
import sys

DEFAULT_DISTANCE = 0.1
DANGEROUS_DIST = 250 
DISTANCE_DANGER_DATA = 100  # Ha a front ennél kisebb -> megállunk, megfordulunk.
SAFE_DISTANCE_DATA = (
    200  # Megállás, meg fordulás után ha ennél nagyobb a front -> elindulunk előre.
)
SERVO_MIN = 0
SERVO_MAX = 200
SERVO_CENTER = 100

STRAIGHT_LINE_FRONT_BACK_SUM_MIN = 2000



GPIO.setmode(GPIO.BOARD)


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

if len(sys.argv) == 1:
    # Varunk a gomb megnyomasara.
    print('Gombra varunk...')
    GPIO.setup(11, GPIO.IN)
    while x := GPIO.input(11): # 1 -> nincs lenyomva. 0 -> le van nyomva
        pass

# Megnyomtak a gombot, varunk 2 mp-et

time.sleep(2)

servo = Servo(12)


def safe(value):
    return (
        value
        if value is not None
        else min(DEFAULT_DISTANCE, value) if value is not None else DEFAULT_DISTANCE
    )


Straight_lines = 0
where_on_straight_line = None
elore()
start_time = time.monotonic()
with open("run_log.txt", "wt") as flog:
    while True:
#        thing = get_thing()
        thing=None
        for i in range(5):
            Disctance_Data = readout()
            if all([x < 10000 for x in readout()]):
                break
        else:
            #        Disctance_Data = readout()
            Disctance_Data = [x if x < 11000 else 0 for x in Disctance_Data] # pyright: ignore[reportPossiblyUnboundVariable]

        # verified sensor order: front, right, back, left
        Front = safe(Disctance_Data[0])
        Rside = safe(Disctance_Data[1])
        Back = safe(Disctance_Data[2])
        Lside = safe(Disctance_Data[3])
        hiba = None

        K_BASE = 0.3  # proporcionalis vezerles szorzotenyezoje

        if (Lside <= DANGEROUS_DIST) and (Rside > DANGEROUS_DIST):
            # Ha kozelebb van a bal oldali fal, mint a veszelyes tavolsag, eros veszkormanyzas jobbra
            print("Emergency steering right")
            steering = SERVO_MIN
        elif (Rside <= DANGEROUS_DIST) and (Lside > DANGEROUS_DIST):
            # Ha kozelebb van a jobb oldali fal, mint a veszelyes tavolsag, eros veszkormanyzas balra
            print("Emergency steering left")
            steering = SERVO_MAX
        else:
            # normalis esetben a ket oldalso szenzor kulonbsegevel aranyos kormanyzas
            hiba = Lside - Rside
            steering = SERVO_CENTER + K_BASE * hiba
            steering = max(SERVO_MIN, min(SERVO_MAX, steering))

        print(
            f"thing={thing} Front={Front} Lside={Lside} Rside={Rside} Back={Back} {hiba=} -> steering={steering}           ",
            end="\n",
        )
        flog.write(f"{time.monotonic()-start_time}\t{Front}\t{Lside}\t{Rside}\t{Back}\t{steering}\n")

        # Itt szamoljuk a megtett koroket. Az egyenes szakaszok veget eszleljuk.
        # Figyelunk arra, hogy az elso es a hatso tavolsagszenzor erteke "eleg nagy" legyen (az auto
        # egyenesben alljon). Ekkor ha az egyenes tavolsag (~ 3 m kell, hogy legyen, mert a palya ~ 3 m
        # hosszu) 2/3-a elott vagyunk, akkor azt mondjuk, hogy az egyenes szakasz elejen vagyunk.
        # Ha pedig a ~ 3 m hossz 1/3-anal kevesebbet mutat az elso tavolsagmero, akkor az egyenes szakasz
        # vegen vagyunk. Ha eszrevesszuk, hogy Eleje -> Veg ugras van (azaz az aktualis egyenes szakasz
        # vegere ertunk), akkor noveljuk az egyenes szakasz szamlalot. 3 kort kell megtenni, ugyhogy az
        # egyenes szakasz szamlalas 12-ig ha eler, akkor megallunk.
        if (Front + Back > STRAIGHT_LINE_FRONT_BACK_SUM_MIN) and (Front < 3000) and (Back < 3000):
            # ellenorizzuk, hogy hol vagyunk az egyenesen
            if Front / (Front + Back) < 0.5:
                # Egyenes vegen vagyunk
                if where_on_straight_line == 'Start':
                    Straight_lines += 1
                    print(Straight_lines)
                where_on_straight_line = 'End'
            if Front / (Front + Back) > 0.6:
                # Egyenes elejen vagyunk
                where_on_straight_line = 'Start'
        servo.set_steering(steering)
        if Straight_lines == 14:
            break
