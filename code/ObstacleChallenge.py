import time
import RPi.GPIO as GPIO
import sys
from GetThing import get_steering_command
from Uart_Disctance_Sensor import readout
from motorcontrol import elore, stop, hatra
from cv2 import inRange, countNonZero
from numpy import array

steering = 85
GPIO.setmode(GPIO.BOARD)
minmagenta = array([125, 0, 125])
maxmagenta = array([255, 80, 255])

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


servo = Servo(12)
servo.set_steering(85)
magentaseen = False
elore()

DEFAULT_DISTANCE = 0.1
DANGEROUS_DIST = 300
DISTANCE_DANGER_DATA = 200

SERVO_MIN = 0
SERVO_MAX = 200
SERVO_CENTER = 100

STRAIGHT_LINE_FRONT_BACK_SUM_MIN = 1500

def safe(value):
    return value if value is not None else DEFAULT_DISTANCE

stw = None
Straight_lines = 0
where_on_straight_line = None
elore()
start_time = time.monotonic()

try:
    with open("run_log.txt", "wt") as flog:
        while True:
            thing = None
            for i in range(5):
                Disctance_Data = readout()
                if all([x < 10000 for x in readout()]):
                    break
            else:
                Disctance_Data = [x if x < 11000 else 0 for x in Disctance_Data]

            Front = safe(Disctance_Data[0])
            Rside = safe(Disctance_Data[1])
            Back = safe(Disctance_Data[2])
            Lside = safe(Disctance_Data[3])

            K_BASE = 0.17

            # ================== NORMÁL + OSZLOP VÉSZKERÜLÉS (eredeti logika) ==================
            if Front < 120 and Rside > Lside:
                print("Emergency steering right")
                steering = SERVO_MIN
            elif Front < 120 and Rside < Lside:
                print("Emergency steering left")
                steering = SERVO_MAX
            else:
                hiba = Lside - Rside
                steering = SERVO_CENTER + K_BASE * hiba
                steering = max(SERVO_MIN, min(SERVO_MAX, steering))

            print(
                f"Front={Front:.0f} Lside={Lside:.0f} Rside={Rside:.0f} Back={Back:.0f} -> steering={steering:.0f}",
                end="\n",
            )
            flog.write(
                f"{time.monotonic()-start_time}\t{Front}\t{Lside}\t{Rside}\t{Back}\t{steering}\n"
            )

            # Vision felülírás
            final_steering = get_steering_command(steering)

            # EREDETI biztonsági front rész (oszlopokhoz)
            if steering == final_steering[0] and Front < 150:
                if Lside > Rside:
                    servo.set_steering(200)
                elif Rside > Lside:
                    servo.set_steering(0)
                stw = time.monotonic()
            else:
                if stw and time.monotonic() - stw < 0.5:
                    continue
                elif stw and time.monotonic() - stw >= 0.5:
                    stw = 0
                servo.set_steering(final_steering[0])

            # ================== EREDETI KÖR SZÁMLÁLÁS ==================
            """
            if (
                (Front + Back > STRAIGHT_LINE_FRONT_BACK_SUM_MIN)
                and (Front < 3000)
                and (Back < 3000)
            ):
                if Front / (Front + Back) < 0.3:
                    if where_on_straight_line == "Start":
                        Straight_lines += 1
                        print(Straight_lines)
                    where_on_straight_line = "End"
                if Front / (Front + Back) > 0.6:
                    where_on_straight_line = "Start"

            if Straight_lines == 12:
                break"""
            if countNonZero(inRange(final_steering[1], minmagenta, maxmagenta)) > 10000:
                magentaseen = True
            elif magentaseen and countNonZero(inRange(final_steering[1], minmagenta, maxmagenta)) < 30:
                Straight_lines += 4
                magentaseen = False
            if Straight_lines == 12:
                while readout()[0] > 700:
                    pass
                break

finally:
    stop()
    GPIO.cleanup()