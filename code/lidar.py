from rplidar import RPLidar
from threading import Thread
from queue import Queue, Empty, Full

lidar = RPLidar('/dev/ttyUSB0')
lidar.start_motor()


running = True
qin = Queue()
qout = Queue()

def get_lidar_data() -> tuple | None:
    """Get data from the LiDAR sensor.
    
    Returns:
        tuple: A tuple containing the minimum distances in the front, right, left, and back directions.
               Returns None if the LiDAR is not running or if no data is available.
    """
    global running
    if not running:
        return None
    try:
        qin.put(None)
        return qout.get(timeout=1)
    except Full:
        qin.queue.clear()
        qin.put(None)
        return qout.get(timeout=1)

def stop_lidar():
    global running
    running = False
    t.join()


def thread_lidar():
    global running
    try:
        for scan in lidar.iter_scans():
            fw = 1024
            rt = 1024
            lt = 1024
            bw = 1024
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
            if not running:
                break
            try:
                if qin.get_nowait() is None:
                    qout.put_nowait((fw, rt, lt, bw))
            except Empty:
                pass
            except Full:
                qout.queue.clear()
                qout.put_nowait((fw, rt, lt, bw))
    finally:
        lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()
        qin.queue.clear()
        qout.queue.clear()
        running = False

t = Thread(target=thread_lidar)
t.start()


if __name__ == '__main__':
    try:
        while True:
            data = get_lidar_data()
            if data:
                fw, rt, lt, bw = data
                print(f"Front: {fw}, Right: {rt}, Left: {lt}, Back: {bw}")
    finally:
        stop_lidar()