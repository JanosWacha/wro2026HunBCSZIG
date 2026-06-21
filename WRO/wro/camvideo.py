from picamera2 import Picamera2
from picamera2.encoders import H264Encoder

picam2 = Picamera2()
encoder = H264Encoder(1000000)
def record(file="test.h264", dir="/home/pi/recordings/"):
    picam2.start_recording(encoder, dir+file)
def stop():
    picam2.stop_recording()
if __name__ == "__main__":
    try:
        record()
        while True:
            pass
    finally:
        stop()
