from Uart_Disctance_Sensor import readout
from servo_control import move_servo
from motorcontrol import elore, hatra, stop
from time import sleep

# ---- Kormany skala ----
# egyenes = 100, teljesen balra = 200, teljesen jobbra = 0
move_servo(100)  # egyenes
steering = 100
sleep(1)
elore()
sleep(1)
stop()

# Ha egy szenzor idotullepest/ervenytelen valaszt ad, a readout() None-t ad
# vissza ahelyett, hogy crashelne. A szenzor 2-450cm (20-4500mm) kozt mer.
# Minden, ami ennel nagyobb (vagy None), egyarant "nincs semmi a kozelben,
# amennyire a szenzor latja" -- ezert mindket esetben ugyanarra a realis
# maximumra vagjuk le, kulonben egy hianyzo/hibas adat oriasi, irrealis
# kilenget okozhatna a kormany-formulaban.
MAX_RANGE = 4500
DEFAULT_DISTANCE = MAX_RANGE

def safe(value):
    if value is None:
        return DEFAULT_DISTANCE
    return min(value, MAX_RANGE)

# ---- Kormanyzasi parameterek (Open Challenge: csak fal-koveteses) ----
K_BASE = 3  # alap erzekenyseg egyenes szakaszon / enyhe elteresnel
K_BOOST = 10      # plusz erzekenyseg, amikor mar nagyon kozel a fal elol
FRONT_THRESH = 800   # ez alatt mar "sarok-kozelsegnek" szamit

while True:
    Disctance_Data = readout()
    # verified sensor order: front, right, back, left
    Front = safe(Disctance_Data[0])
    Rside = safe(Disctance_Data[1])
    Back = safe(Disctance_Data[2])
    Lside = safe(Disctance_Data[3])

    # Vesztelyhelyzet: ha barmelyik oldal/elol nagyon kozel van, hatrameneb.
    if Lside <= 15 or Rside <= 15 or Front <= 30:
        hatra()
    else:
        elore()

    # Folytonos, aranyos kormanyzas: a bal/jobb oldali tavolsag
    # KULONBSEGEHEZ igazodik. Minel kozelebb van elol egy fal, annal
    # ERZEKENYEBBEN reagal UGYANARRA a kulonbsegre -- igy a sarokban,
    # amikor mar kozel van a fal, sokkal elesebben fordul.
    urgency = max(0, FRONT_THRESH - Front) / FRONT_THRESH
    urgency = min(urgency, 1)
    K_effective = K_BASE + K_BOOST * urgency

    hiba = Lside - Rside
    steering = 100 + K_effective * hiba
    steering = max(0, min(200, steering))

    print(f"Front={Front} Lside={Lside} Rside={Rside} Back={Back} -> steering={round(steering, 1)}")
    move_servo(steering)