from gpiozero import Button
from signal import pause
button = Button(17)
import os
button.when_pressed = lambda: [print("y"), exit(), os.system("/usr/bin/python3 /home/pi/Documents/wro/decide.py"), exit()]
pause()
