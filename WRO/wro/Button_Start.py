from gpiozero import Button
from signal import pause
#Button setup
button = Button(17)
import os
#Starting the decide.py when we press the button.
button.when_pressed = lambda: [os.system("/usr/bin/python3 /home/pi/Documents/wro/decide.py"), exit()]
pause()
