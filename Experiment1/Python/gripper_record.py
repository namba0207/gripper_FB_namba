# Arduino_gripper_con.inoとセット！！
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
        self.bendingValue_int = 400
        self.num_int = 127
        ip = "192.168.1.199"
        self.ser = serial.Serial("COM8", 115200)
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
        startTime = time.perf_counter()
        while True:
            line = self.ser.readline().decode("utf-8").rstrip()
            self.data_parts = line.split(",")
            self.bendingValue_int = int(
                400 - int(self.data_parts[0].rstrip()) / 2200 * 400
            )
            if self.bendingValue_int > 400:
                self.bendingValue_int = 400
            elif self.bendingValue_int < 0:
                self.bendingValue_int = 0
            code, ret = self.arm.getset_tgpio_modbus_data(
                self.datal.ConvertToModbusData(self.bendingValue_int)
            )

    def loop(self):
        try:
            # code5//loadcell読み取り
            while True:
                self.num = int(self.datal.loadcell_val * 1000)
                if self.num > 200:
                    self.num = 200
                elif self.num < 0:
                    self.num = 0
                self.num_int = int(self.num / (200 - 0) * (255 - 127) + 127)
                self.ser.write(bytes([self.num_int]))
                time.sleep(0.005)
        except KeyboardInterrupt:
            print("except KeyboardInterrupt")
            self.ser.close()
            sys.exit()


if __name__ == "__main__":
    text_class = Text_class()
    time.sleep(0.5)
    start_time = time.perf_counter()
    while True:
        try:
            data1 = text_class.data_parts[0].rstrip()
            data2 = text_class.num_int
            data3 = time.perf_counter() - start_time
            # 新しいデータをCSVファイルに追記
            with open("data0115_1.csv", "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([data1, data2, data3])
            time.sleep(0.005)
        except KeyboardInterrupt:
            print("KeyboardInterrupt Stop:text")
            break
