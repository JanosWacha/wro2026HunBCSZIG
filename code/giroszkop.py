"""
BNO055 szenzor - Z tengely (heading) kiolvasó modul
Raspberry Pi + Adafruit BNO055, I2C kapcsolaton keresztül

Használat másik fájlból:
    from bno055_heading import get_z_tengely

    z = get_z_tengely()
    if z is not None:
        print(z)
"""

import time
import board
import busio
import adafruit_bno055

_i2c = None
_sensor = None


def _szenzor_inicializalasa():
    """Csak első hívásnál kapcsolódik a szenzorhoz, utána újrahasználja."""
    global _i2c, _sensor
    if _sensor is None:
        _i2c = busio.I2C(board.SCL, board.SDA)
        _sensor = adafruit_bno055.BNO055_I2C(_i2c)
    return _sensor


def get_z_tengely(probalkozasok=3):
    """
    Visszaadja a szenzor aktuális Z tengely körüli elfordulását (heading),
    fokban, 0-360 között.

    Ha átmeneti I2C hiba van (pl. laza vezeték), párszor újrapróbálja.
    Ha végül sem sikerül olvasni, None-t ad vissza - EZT MINDIG ELLENŐRIZD
    a hívó kódban, mielőtt felhasználod az értéket!
    """
    sensor = _szenzor_inicializalasa()

    for _ in range(probalkozasok):
        try:
            heading, roll, pitch = sensor.euler
            if heading is not None:
                return (heading+180)%360
        except OSError:
            time.sleep(0.05)

    return None


# Ez a rész csak akkor fut le, ha ezt a fájlt közvetlenül futtatod
# (python3 bno055_heading.py). Ha másik fájlból importálod, ez kimarad.
if __name__ == "__main__":
    print("BNO055 elindítva. Ctrl+C a kilépéshez.\n")

    hiba_szamlalo = 0
    try:
        while True:
            z = get_z_tengely()

            if z is not None:
                print(f"Z tengely (heading): {z:6.1f}°           ", end="\r")
                hiba_szamlalo = 0
            else:
                hiba_szamlalo += 1
                print(f"Nem sikerült olvasni a szenzort. ({hiba_szamlalo}. hiba egymás után)")
                if hiba_szamlalo >= 10:
                    print("Túl sok egymás utáni hiba - ellenőrizd a vezetékeket "
                          "(VIN, GND, SDA, SCL)!")

    except KeyboardInterrupt:
        print("\nLeállítva.")