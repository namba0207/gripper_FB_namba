#!/usr/bin/env python3
import time

import serial

if __name__ == "__main__":
    ser = serial.Serial("COM6", 115200, timeout=1)
    ser.flush()
    # A = str(100) + "\n"
    # B = str(333) + "\n"
    while True:
        # ser.write(A.encode())
        # ser.write(B.encode())
        line = ser.readline().decode("utf-8").rstrip()
        print(line)
        time.sleep(0.005)
