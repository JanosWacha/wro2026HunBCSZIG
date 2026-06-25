from RPi import GPIO
from sys import argv
from time import monotonic
GPIO.setmode(GPIO.BOARD)


def gomb_megnyomva():
    # 1 -> nincs lenyomva. 0 -> le van nyomva
    return GPIO.input(11) == 0


GPIO.setup(11, GPIO.IN)
if len(argv) == 1:
    # Varunk a gomb megnyomasara.
    print("Gombra varunk...")
    sw = None
    while True:
        if gomb_megnyomva():
            if not sw:
                sw = monotonic()
            elif monotonic() - sw >= 0.5:
                break
        elif sw:
            sw = None
import decide