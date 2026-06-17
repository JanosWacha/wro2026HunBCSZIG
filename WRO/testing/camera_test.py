import picamera2

cam = picamera2.Picamera2()
cam.start_preview(picamera2.Preview.NULL)
cam.start()
print(cam.capture_array())

