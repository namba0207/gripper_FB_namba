#!/usr/bin/env python3
import serial
import time
if __name__ == '__main__':
    ser = serial.Serial('/dev/cu.usbmodem14311', 115200, timeout=1)
    ser.flush()
    while True:
        ser.write(b"r\n")
        line = ser.readline().decode('utf-8').rstrip()

        if line.strip():  # 空でない場合のみ処理
            # print(float(line.replace('\n', '')))
            force_data = float(line.replace('\n', ''))*0.0001
            print(force_data)

        time.sleep(0.01)