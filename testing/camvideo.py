from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from datetime import datetime

picam2 = Picamera2()
#picam2.configure(picam2.create_video_configuration(main={"size": (3280, 2464)}))
encoder = H264Encoder(1000000)
def record(file="record-<DATE>.h264", dir="/home/pi/recordings/"):
    picam2.start_recording(encoder, dir+file.replace("<DATE>", datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))
def stopcam():
    picam2.stop_recording()
if __name__ == "__main__":
    from motorcontrol import elore, stop
    try:
        record("test-<DATE>.h264")
        elore()
        while True:
            pass
    finally:
        stopcam()
        stop()
