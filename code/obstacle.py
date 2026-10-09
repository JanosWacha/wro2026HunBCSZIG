#!/usr/bin/env python3

from Uart_Disctance_Sensor import readout
from detectcolor import detect_color, picam2
from motorcontrol import Motor
import time
import RPi.GPIO as GPIO
from giroszkop import get_z_tengely
import ledcontrol
from threading import Thread
import stream
from sys import argv
from picamera2 import Picamera2
from libcamera import Transform
#from sys import path
#path.append("/usr/lib/python3/dist-packages/")
btcheck=True
gui=False
if len(argv) > 1:
    if "b" in argv[1]:
        btcheck = False
    if "g" in argv[1]:
        gui = True
goal_dir = get_z_tengely()
steering = 150
balp = 0
jobbp = 0
tm1 = None
def gomb():
    global tm1
    if not GPIO.input(17):
        if not tm1:
            tm1 = time.monotonic()
        elif time.monotonic()-tm1 >= 0.5:
            return False
    else:
        tm1 = None
    return True
try:
    steering = 150
    from servo import Servo
    GPIO.setup(17, GPIO.IN)
    tm = time.monotonic()
    s0 = "0"
    s1 = "1"
    print(end="Gombnyomásra vár" if btcheck else "\r")
    while btcheck and gomb():
        if time.monotonic()-tm > 0.25:
            s1 = s0
            s0 = "0" if s0 == "1" else "1"
        ledcontrol.set_led_status(0, s0)
        ledcontrol.set_led_status(1, s1)
    ledcontrol.reset_leds()
    tm = time.monotonic()
    kanyar=False
    state="Egyenes"
    where_on_straight_line = ""
    kanyarsorszam = 0
    servo = Servo(log=False)
    servo.set_steering(150)
    Straight_lines = 0
    r = readout()
    r = readout()
    z = get_z_tengely()
    z = get_z_tengely()
    def ro():
        return r
    def gr():
        return z
    def kn(r):
        return str(kanyarsorszam)+". "+state+" "+str(Straight_lines)+where_on_straight_line + " " + str(time.monotonic()-tm)
    if gui:
        t = Thread(target=stream.start_server, kwargs={"pic2": picam2, "ro": ro, "gr": gr, "kn": kn, "sv": servo.get_steering})
        t.start()
    time.sleep(1)
    m = Motor()
    m.elore()
    K=2
    zmap=0
    cntkanyar = 0
    starttime = time.monotonic()
    def safez(z, lastz):
        return z if z else lastz-zmap
    def safer(r, lastr):
        for i in range(4):
            if not r[i]:
                r[i] = lastr[i]
        return r
    dirn = None
    tm2 = 0
    gd = 180
    while kanyarsorszam < 12:
        if not gomb():
            print("Gomb stop")
            exit()
        if time.monotonic()-tm2 < 0.3:
            continue
        if time.monotonic()-tm2 > 0.3 and time.monotonic()-tm2 < 0.5:
            servo.go_forward()
            continue
        r = safer(readout(), r)
        z = (safez(get_z_tengely(), z)+zmap)%360
        if r[3] / (a:=r[3] + r[0]) < 0.3 and a > 1000:
            # Egyenes vegen vagyunk
            if where_on_straight_line == 'Start':
                Straight_lines += 1
            where_on_straight_line = 'End'
        if r[3] / (a:=r[3] + r[0]) > 0.6 and a > 1000:
            # Egyenes elejen vagyunk
            where_on_straight_line = 'Start'
        if r[3] < 150:
            m.hatra()
            servo.set_steering((300-steering)*0.5)
            while (r:=readout())[3] < 300 and r[0]>100:pass
            m.elore()
        if r[3] < 1500 and where_on_straight_line == 'End' and time.monotonic()-tm > 2: # pyright: ignore[reportOperatorIssue]
            if r[1] > 600 and dirn != "r":
                if cntkanyar > 0:
                    if not kanyar:
                        zmap = zmap+90
                        kanyar=True
                        cntkanyar = 5
                        kanyarsorszam += 1
                        state = "Kanyar (bal)"
                    dirn = "l"
                    tm = time.monotonic()
                else:
                    cntkanyar += 1
            elif r[2] > 600 and dirn != "l":
                if cntkanyar > 0:
                    if not kanyar:
                        zmap = zmap-90
                        kanyar=True
                        cntkanyar = 5
                        kanyarsorszam += 1
                        state = "Kanyar (jobb)"
                    dirn = "r"
                    tm = time.monotonic()
                else:
                    cntkanyar += 1
        elif r[0]+r[3] > 1500 or where_on_straight_line == 'Start':
            if cntkanyar>2:
                tm = time.monotonic()
                cntkanyar -= 1
            else:
                cntkanyar = 0
            kanyar=False
            state = "Egyenes"

        balp = 0
        jobbp = 0
        balp += r[2] * 0.1
        jobbp += r[1] * 0.1
        if goal_dir > z: # pyright: ignore[reportOptionalOperand, reportOperatorIssue]
            balp += abs(goal_dir - z)*15 # pyright: ignore[reportOptionalOperand, reportOperatorIssue]
        elif goal_dir < z: # pyright: ignore[reportOptionalOperand, reportOperatorIssue]
            jobbp += abs(goal_dir - z)*15 # pyright: ignore[reportOptionalOperand, reportOperatorIssue]
        d = detect_color()
        if d == "green":
            print(d)
            jobbp += 10
            tm2 = time.monotonic()
        elif d == "red":
            print(d)
            balp += 10
            tm2 = time.monotonic()
        steering = abs(jobbp-balp)
        if balp > jobbp:
            steering = 150 - steering
        else:
            steering = 150 + steering
        servo.set_steering(steering)
    print("Utolsó kanyar")
    while True:
        r = readout()
        z = get_z_tengely()
        if r[3] < 150:
            m.hatra()
            servo.set_steering((300-steering)*0.5)
            while (r:=readout())[3] < 300 and r[0]>100:pass
            m.elore()
        balp = 0
        jobbp = 0
        balp += r[2] * 1
        jobbp += r[1] * 1
        if goal_dir > z: # pyright: ignore[reportOperatorIssue]
            balp += abs(goal_dir - z)*15 # pyright: ignore[reportOperatorIssue]
        elif goal_dir < z: # pyright: ignore[reportOperatorIssue]
            jobbp += abs(goal_dir - z)*15 # pyright: ignore[reportOperatorIssue]
        steering = abs(jobbp-balp)
        if balp > jobbp:
            steering = 150 - steering
        else:
            steering = 150 + steering
        servo.set_steering(steering)
        if r[3]-r[0] < 100 and time.monotonic()-tm > 5:
            break
    servo.go_forward()
    m.stop()
finally:
    m.stop() # pyright: ignore[reportPossiblyUnboundVariable]
    servo.go_forward() # pyright: ignore[reportPossiblyUnboundVariable]
    GPIO.cleanup()
    if gui:stream.stop_server()