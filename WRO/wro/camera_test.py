import picamera2
import time

N_READOUT = 100

cam = picamera2.Picamera2()
cam.start_preview(picamera2.Preview.NULL)
cam.start()

t0 = time.monotonic()
for i in range(N_READOUT):
    cam.capture_array()
t1 = time.monotonic()
print(f'Acquired {N_READOUT} images in {t1-t0:.3f} seconds')
print(f'Camera readout frequency: {N_READOUT/(t1-t0):.3f} Hz')

print(cam.capture_file("test.png"))

