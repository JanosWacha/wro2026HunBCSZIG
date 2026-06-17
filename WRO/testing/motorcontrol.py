from gpiozero import DigitalOutputDevice as dod
e = dod(21)
h = dod(20)
def elore():
    h.off()
    e.on()
def hatra():
    e.off()
    h.on()
def stop():
    e.off()
    h.off()
def demo():
    while (i:=input("Előre/Hátra/Stop/Kilép[e/h/s/q]").strip().lower()) != "q":
        if i == "e":
            elore()
        elif i == "h":
            hatra()
        else:
            stop()
    stop()
    print("Viszlát")
if __name__ == "__main__":
    demo()
