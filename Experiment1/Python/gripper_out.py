# 反力そのままフィードバック
import csv  # 記録用
import sys
import threading
import time

import numpy as np
import serial
from ArmWrapper1000 import ArmWrapper
from xarm.wrapper import XArmAPI

class Text_class:
    def __init__(self):
        self.pos1 = 500
        self.pos = 425
        self.num_int = 127
        self.vol1 = 127
        ip = "192.168.1.199"
        arduino_port = "COM8"
        baud_rate = 115200
        self.ser = serial.Serial(arduino_port, baud_rate)
        not_used = self.ser.readline()
        self.arm = XArmAPI(ip)
        time.sleep(0.5)
        if self.arm.warn_code != 0:
            self.arm.clean_warn()
        if self.arm.error_code != 0:
            self.arm.clean_error()
        self.arm.motion_enable(True)
        self.arm.set_mode(0)
        self.arm.set_state(0)
        self.datal = ArmWrapper(True, ip)
        thr1 = threading.Thread(target=self.loop)
        thr1.setDaemon(True)
        thr1.start()
        thr2 = threading.Thread(target=self.thread)
        thr2.setDaemon(True)
        thr2.start()

    def thread(self):
        with open('/Users/sanolab/Documents/python/仮想環境/data.csv') as f:
            reader = csv.reader(f)
            self.l = [row for row in reader]
        self.count = 0
        while True:
            self.bendingValue_int = int(
                    400
                    - int(self.l[self.count][0])
                    / 2600
                    * 400
                )
            if self.bendingValue_int > 400:
                self.bendingValue_int = 400
            elif self.bendingValue_int < 0:
                self.bendingValue_int = 0
            code, ret = self.arm.getset_tgpio_modbus_data(
                self.datal.ConvertToModbusData(self.bendingValue_int)
            )
            count += 1
            time.sleep(0.005)

    def loop(self):
        while True:
            self.ser.write(bytes([self.l[self.count][0]]))
            time.sleep(0.005)

if __name__ == "__main__":
    text_class = Text_class()
    time.sleep(0.5)
    while True:
        try:
            time.sleep(0.005)
        except KeyboardInterrupt:
            print("KeyboardInterrupt Stop:text")
            break