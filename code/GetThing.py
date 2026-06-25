import cv2
import numpy as np
from picamera2 import Picamera2
# ============ PICAMERA2 SETUP ============
cam = Picamera2()
width, height = 320, 180

w, h = cam.sensor_modes[2]["size"]
cam.configure(
    cam.create_video_configuration(
        main={"format": 'XRGB8888', "size": (width, height)}))
cam.start()

# ============ PIROS -- szélesebb, biztonságosabb tartomány ============
RED_LOWER1 = np.array([0, 140, 80])
RED_UPPER1 = np.array([8, 255, 255])
RED_LOWER2 = np.array([172, 140, 80])
RED_UPPER2 = np.array([180, 255, 255])

# ============ ZÖLD -- kiterjesztve sárgászöld és sötétebb zöld felé is ============
GREEN_LOWER = np.array([35, 60, 40])
GREEN_UPPER = np.array([90, 255, 255])

# ============ BŐRSZÍN -- explicit kizárás ============
SKIN_LOWER = np.array([0, 30, 60])
SKIN_UPPER = np.array([25, 150, 255])

KERNEL = np.ones((5, 5), np.uint8)

# ============ SERVO BEÁLLÍTÁSOK ============
SERVO_CENTER = 100
SERVO_MIN = 0
SERVO_MAX = 200
NO_OVERRIDE = -1   # ezt adjuk vissza, ha a fő program vezérelje a servot

# ============ ÉRZÉKENYSÉG ============
K = 0.002
BASE_K = 0.01

# ============ KÜSZÖBÖK ============
MIN_AREA_NOISE = 250          # zajszűrés
MIN_AREA_TO_REACT = 2000      # "túl messze, ne reagáljunk" -- csak KÖZÉPEN lévő pylonra
AREA_AT_50CM = 6000           # "most már erősen kanyarodjunk" referenciapont
SAFE_PASS_RATIO = 0.1    # safe-pass zóna küszöb -- duplázva (volt: 0.04)

# Mennyire kell oldalra csúsznia a pylonnak (px), hogy "oldalt van" számítson,
# és emiatt felülírja a MIN_AREA_TO_REACT-et akkor is, ha messze van.
SIDE_OFFSET_OVERRIDE_PX = 40

DIRECTIONAL_DAMPING = 0.6     # jó oldalon mennyire csillapítható a magnitude


def get_frame_bgr():
    frame = cam.capture_array()
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    return frame_bgr


def _clean_mask(mask):
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL, iterations=2)
    return mask


def _largest_contour_info(mask, min_area):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return 0
    c = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(c)
    if area < min_area:
        return 0
    x, y, w, h = cv2.boundingRect(c)
    return {"area": area, "bbox": (x, y, w, h)}


def detect_pylon(frame_bgr, min_area=MIN_AREA_NOISE):
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

    red_mask_raw = (
        cv2.inRange(hsv, RED_LOWER1, RED_UPPER1) |
        cv2.inRange(hsv, RED_LOWER2, RED_UPPER2)
    )
    skin_mask = cv2.inRange(hsv, SKIN_LOWER, SKIN_UPPER)
    red_mask = cv2.bitwise_and(red_mask_raw, cv2.bitwise_not(skin_mask))
    red_mask = _clean_mask(red_mask)

    green_mask = cv2.inRange(hsv, GREEN_LOWER, GREEN_UPPER)
    green_mask = _clean_mask(green_mask)

    red_info = _largest_contour_info(red_mask, min_area)
    green_info = _largest_contour_info(green_mask, min_area)

    result = {"color": None, "area": 0, "bbox": None, "center_x": None}

    if red_info and green_info:
        winner, color = (red_info, "red") if red_info["area"] >= green_info["area"] else (green_info, "green")
    elif red_info:
        winner, color = red_info, "red"
    elif green_info:
        winner, color = green_info, "green"
    else:
        return result

    x, y, w, h = winner["bbox"]
    result.update({
        "color": color,
        "area": winner["area"],
        "bbox": (x, y, w, h),
        "center_x": x + w // 2,
    })
    return result


def compute_avoidance_servo(pylon_result, frame_width):
    """
    Visszaadás: (servo_angle:int, is_avoiding:bool, reason:str)
    servo_angle == -1 (NO_OVERRIDE)  ->  a fő program vezérelje a servot
        (pl. wall-following), ez NEM jelent kerülést.
    reason: "no_pylon" | "too_far" | "safe_pass" | "avoiding"
    """
    color = pylon_result["color"]
    if color is None:
        return NO_OVERRIDE, False, "no_pylon"

    area = pylon_result["area"]
    frame_center_x = frame_width / 2
    offset = pylon_result["center_x"] - frame_center_x  # + jobbra, - balra

    # --- "Túl messze" csak akkor blokkol, ha a pylon KÖZÉPEN van.
    #     Ha már jelentősen oldalra csúszott, az azt jelenti hogy már
    #     kerülés közben vagyunk -- akkor is reagáljunk, ha area kicsi. ---
    is_significantly_sideways = abs(offset) > SIDE_OFFSET_OVERRIDE_PX
    if area < MIN_AREA_TO_REACT and not is_significantly_sideways:
        return NO_OVERRIDE, False, "too_far"

    if color == "red":
        directional_offset = -offset   # jó oldal (jobbra, offset>0) -> negatív
    else:
        directional_offset = offset    # jó oldal (balra, offset<0) -> negatív

    # directional_offset NEGATÍV -> jó oldalon van
    # directional_offset POZITÍV -> rossz oldalon van

    # --- Safe-pass zóna: csak akkor, ha JÓ OLDALON van és elég messze
    #     a középvonaltól a közelségéhez képest ---
    safe_ratio = -directional_offset / max(area, 1)
    if safe_ratio > SAFE_PASS_RATIO:
        return NO_OVERRIDE, False, "safe_pass"

    # --- Aktív kerülés ---
    closeness = min(area / AREA_AT_50CM, 1.5)
    base = BASE_K * area * closeness
    directional_term = K * area * directional_offset

    if directional_term >= 0:
        magnitude = base + directional_term
    else:
        magnitude = base + directional_term * DIRECTIONAL_DAMPING
        magnitude = max(magnitude, base * (1 - DIRECTIONAL_DAMPING))
    Smoothness = magnitude * 1.2
    if color == "green":
        steering = SERVO_CENTER + magnitude
    else:
        steering = SERVO_CENTER - magnitude

    steering = max(SERVO_MIN, min(SERVO_MAX, steering))
    return int(round(steering)), True, "avoiding"


def get_steering_command(wall_following_servo_angle):
    frame_bgr = get_frame_bgr()
    frame_height, frame_width = frame_bgr.shape[:2]
    pylon = detect_pylon(frame_bgr)
    avoid_angle, is_avoiding, reason = compute_avoidance_servo(pylon, frame_width)

    if is_avoiding:
        return avoid_angle, frame_bgr
    return wall_following_servo_angle, frame_bgr


if __name__ == "__main__":
    while True:
        frame = get_frame_bgr()

        frame_width = frame.shape[1]
        pylon = detect_pylon(frame)
        servo_angle, is_avoiding, reason = compute_avoidance_servo(pylon, frame_width)

        if pylon["color"]:
            x, y, w, h = pylon["bbox"]
            offset = pylon["center_x"] - frame_width / 2
            print(f"color={pylon['color']} area={pylon['area']:.0f} offset={offset:.0f} "
                  f"servo={servo_angle} reason={reason}")
        print(f"servo={servo_angle} ({reason})")
        cv2.putText(frame, f"servo={servo_angle} ({reason})", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    cam.stop()