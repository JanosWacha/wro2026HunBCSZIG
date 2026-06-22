from gpiozero import Button
pause = True
b = Button(17)
def fgv():
    b.close()
    global pause
    pause = False
b.when_pressed = fgv
while pause:
    pass
