from gpiozero import Button
from signal import pause
button = Button(17)
import os
button.when_pressed = lambda: [os.system("/usr/bin/python3 /home/pi/Documents/wro/decide.py"), exit()]
pause()
