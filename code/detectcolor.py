import cv2
import numpy as np
from matplotlib.pyplot import imsave
from libcamera import Transform # pyright: ignore[reportAttributeAccessIssue]
from picamera2 import Picamera2

# ---- Beállítható értékek ----
MIN_COLOR_RATIO = 0.005  # a teljes kép legalább 2%-a legyen az adott színű, különben "no"
MIN_COLUMN_RATIO = 0.002  # egy oszlop területének legalább 2%-a legyen az adott színű

# HSV tartományok (OpenCV: H 0-179, S 0-255, V 0-255)
GREEN_LOW, GREEN_HIGH = (40, 70, 70), (85, 255, 255)
RED_LOW1, RED_HIGH1 = (0, 120, 80), (6, 255, 255)      # a piros két részre szakad a H skálán
RED_LOW2, RED_HIGH2 = (172, 120, 80), (179, 255, 255)

# ---- Kamera egyszeri inicializálása ----
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration(main={"size": (205, 154), "format": "RGB888"}, raw={"size": picam2.sensor_resolution}, transform=Transform(hflip=True, vflip=True)))
picam2.start()
arr = picam2.capture_array()
h = 205
imsave("test2.jpg", arr[int(h/2-31):int(h/2+2.5), 10:144])


_kernel = np.ones((5, 5), np.uint8)


def _clean(mask):
    """Zajszűrés: kis pöttyök eltávolítása, apró lyukak betömése."""
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, _kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, _kernel)
    return mask


def detect_color():
    """Visszatérési érték: 'green', 'red' vagy 'no'."""
    frame = picam2.capture_array()  # "RGB888" formátumnál a tömb BGR sorrendű (OpenCV-kompatibilis)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    green_mask = _clean(cv2.inRange(hsv, GREEN_LOW, GREEN_HIGH))
    red_mask = _clean(cv2.inRange(hsv, RED_LOW1, RED_HIGH1) | cv2.inRange(hsv, RED_LOW2, RED_HIGH2))

    total = green_mask.size
    green_count = cv2.countNonZero(green_mask)
    red_count = cv2.countNonZero(red_mask)
    green_ok = green_count / total >= MIN_COLOR_RATIO
    red_ok = red_count / total >= MIN_COLOR_RATIO

    # egyik színből sincs elég
    if not green_ok and not red_ok:
        return "no"

    # melyikből van több?
    if green_ok and (not red_ok or green_count >= red_count):
        winner, mask = "green", green_mask
        allowed_columns = (1, 2, 3)   # két középső + jobb oldali
    else:
        winner, mask = "red", red_mask
        allowed_columns = (0, 1, 2)   # bal oldali + két középső

    # felső negyed levágása
    h, w = mask.shape
    mask = mask[int(h/2-31):int(h/2+2.5), :]

    # 4 egyenlő függőleges oszlop
    col_w = w // 4
    for i in allowed_columns:
        column = mask[:, i * col_w:(i + 1) * col_w]
        if cv2.countNonZero(column) / column.size >= MIN_COLUMN_RATIO:
            return winner

    return "no"


if __name__ == "__main__":
    try:
        print(detect_color())
    finally:
        picam2.stop()