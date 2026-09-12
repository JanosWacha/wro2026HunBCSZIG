from rplidar import RPLidar
from threading import Thread

lidar = RPLidar('/dev/ttyUSB0')

fw = 1024
rt = 1024
lt = 1024
bw = 1024
running = True


def thread_lidar():
    global fw
    global rt
    global lt
    global bw
    global running
    try:
        for scan in lidar.iter_scans():
            for (_, angle, distance) in scan:
                if distance > 0:
                    if angle >= 45 and angle < 135:
                        rt = min(rt, distance)
                    elif angle >= 135 and angle < 225:
                        fw = min(fw, distance)  
                    elif angle >= 225 and angle < 315:
                        bw = min(bw, distance)
                    elif angle >= 315 or angle < 45:
                        lt = min(lt, distance)
    finally:
        lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()
        running = False

Thread(target=thread_lidar).start()


if __name__ == '__main__':
    while running:
        print(f"Front: {fw}, Right: {rt}, Left: {lt}, Back: {bw}")