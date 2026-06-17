import serial
import time

devices = ['/dev/ttyS0', '/dev/ttyAMA2', '/dev/ttyAMA4', '/dev/ttyAMA5']

sers = [serial.Serial(d, timeout=0.3) for d in devices]

def readout():
    out = []
    for iser, ser in enumerate(sers):
        ser.flush()
        ser.read_all()
        ser.write(b'\x55')
        try:
            result = ser.read(2)
        except TimeoutError:
            print(f'{iser} ({devices[iser]}): <timeout>')
            continue
        if len(result) < 2:
            print(f'{iser} ({devices[iser]}): <invalid>')
            continue
        out.append(result[1] + (result[0] << 8))

    return out

while True:
    print('-------------------------')
    readout()
    time.sleep(2)

        
