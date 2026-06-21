from os import system
from gpiozero import Button
from time import sleep
from signal import pause

b = Button(17)
b.when_released = lambda: [sleep(1), system("python /home/pi/Documents/wro/decide.py"), exit()]
pause()
