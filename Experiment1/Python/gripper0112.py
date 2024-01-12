# Arduino_gripper_out.inoとセット！！
import csv  # 記録用
import struct
import threading
import time

import numpy as np
import serial
from ArmWrapper1000 import ArmWrapper
from xarm.wrapper import XArmAPI


class Text_class:
    def __init__(self):
        self.bendingValue2 = 0
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
        thr1 = threading.Thread(target=self.moveloop)
        thr1.setDaemon(True)
        thr1.start()
        thr2 = threading.Thread(target=self.sendloop)
        thr2.setDaemon(True)
        thr2.start()
        thr3 = threading.Thread(target=self.receiveloop)
        thr3.setDaemon(True)
        thr3.start()

    # 記録データからグリッパー動かす
    def moveloop(self):
        with open(
            "C:\\Users\\SANOLAB\\Documents\\GitHub\\gripper_FB_namba\\data0112_100BPM.csv"
        ) as f1:
            reader = csv.reader(f1)
            self.l1 = [row for row in reader]
        self.count = 0
        self.start_time = time.perf_counter()
        while True:
            self.bendingValue_int = int(400 - int(self.l1[self.count][0]) / 2600 * 400)
            if self.bendingValue_int > 400:
                self.bendingValue_int = 400
            elif self.bendingValue_int < 0:
                self.bendingValue_int = 0
            code, ret = self.arm.getset_tgpio_modbus_data(
                self.datal.ConvertToModbusData(self.bendingValue_int)
            )
            self.timer = time.perf_counter() - self.start_time
            # print(self.l[self.count][0], self.l[self.count][1], self.timer)
            self.count += 1
            time.sleep(0.0005)

    # 記録データをArduinoへ送る
    def sendloop(self):
        with open(
            "C:\\Users\\SANOLAB\\Documents\\GitHub\\gripper_FB_namba\\data0112_100BPM.csv",
            "r",
        ) as f2:
            reader = csv.reader(f2)
            for row in reader:
                value = int(row[0])
                # print(value)
                self.send_data(value)
                time.sleep(0.005)

    # Arduinoからデータを受け取る
    def receiveloop(self):
        while True:
            self.line = self.ser.readline().decode("utf-8").rstrip()
            # self.data_parts = self.line.split(",")
            # self.bendingValue = self.data_parts[0].rstrip()
            print(self.line)
            # time.sleep(0.000001)

    def send_data(self, data):
        self.binary_data = struct.pack("!i", data)
        self.ser.write(self.binary_data)


if __name__ == "__main__":
    text_class = Text_class()
    while True:
        try:
            time.sleep(0.005)
        except KeyboardInterrupt:
            print("KeyboardInterrupt Stop:text")
            break
