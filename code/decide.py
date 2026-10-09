from Uart_Disctance_Sensor import readout

readout()
r = readout()
dec = r[0] + r[3] < 20
if dec:
    print("Obstacle")
    import obstacle
else:
    print("Open")
    import main