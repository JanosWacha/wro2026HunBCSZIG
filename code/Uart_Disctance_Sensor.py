import serial
import time

devices = ["/dev/ttyS0", "/dev/ttyAMA3", "/dev/ttyAMA4", "/dev/ttyAMA5"]

# sensors (verified order): front, left, right, back

sers = [serial.Serial(d, timeout=0.3) for d in devices]

# emptying the buffers
for ser in sers:
    ser.flush()
    ser.read_all()

def readout():
    """Read out the distance sensors one-by-one, return a list of distances in mm.
    Always returns a list of length 4 (front, left, right, back), in that fixed order.
    If a sensor times out or sends an invalid reply, its slot is set to None
    instead of being skipped, so the indices never shift around."""
    out = [0, 0, 0, 0]
    for iser, ser in enumerate(sers):
        ser.read_all()
        ser.write(b"\x55")
        try:
            result = ser.read(2)
        except TimeoutError:
            print(f"{iser} ({devices[iser]}): <timeout>")
            continue
        if len(result) < 2:
            print(f"{iser} ({devices[iser]}): <invalid>: {result}")
            continue
        out[iser] = result[1] + (result[0] << 8)
    return out


if __name__ == "__main__":
    print('Performing readout frequency measurement...', end='', flush=True)
    N_READOUT = 20
    t0 = time.monotonic()
    for i in range(N_READOUT):
        readout()
    t1 = time.monotonic()
    print('done.')
    print(f'{N_READOUT} readouts in {t1-t0:.3f} seconds.')
    print(f'Readout frequency: {N_READOUT/(t1-t0):.2f} Hz.')
    while True:
        front, right, back, left = readout()
        print(f'{front=:.0f} {back=:.0f} {right=:.0f} {left=:.0f} l-r={left-right:.0f}                    \r', end='')
