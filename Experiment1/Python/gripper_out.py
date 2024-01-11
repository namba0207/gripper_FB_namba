# Arduino_gripper_out.inoとセット！！
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
        # thr3 = threading.Thread(target=self.receiveloop)
        # thr3.setDaemon(True)
        # thr3.start()

    # 記録データからグリッパー動かす
    def moveloop(self):
        start_time = time.perf_counter()
        with open(
            "C:\\Users\\SANOLAB\\Documents\\GitHub\\gripper_FB_namba\\data1.csv"
        ) as f:
            reader = csv.reader(f)
            self.l = [row for row in reader]
        self.count = 0
        # time.sleep(0.1)
        while True:
            self.bendingValue_int = int(400 - int(self.l[self.count][0]) / 2600 * 400)
            if self.bendingValue_int > 400:
                self.bendingValue_int = 400
            elif self.bendingValue_int < 0:
                self.bendingValue_int = 0
            code, ret = self.arm.getset_tgpio_modbus_data(
                self.datal.ConvertToModbusData(self.bendingValue_int)
            )
            # print(int(self.l[self.count][0]))
            self.count += 1
            time.sleep(0.005)

    # 記録データをArduinoへ送る
    def sendloop(self):
        with open(
            "C:\\Users\\SANOLAB\\Documents\\GitHub\\gripper_FB_namba\\data1.csv"
        ) as f:
            reader = csv.reader(f)
            self.l = [row for row in reader]
        self.count2 = 0
        while True:
            self.bendingValue2 = int(int(self.l[self.count2][0]) / 2600 * 255)
            if self.bendingValue2 > 255:
                self.bendingValue2 = 255
            elif self.bendingValue2 < 0:
                self.bendingValue2 = 0
            self.ser.write(bytes([self.bendingValue2]))
            # print(self.l[self.count2][0], self.bendingValue2)
            self.count2 += 1
            time.sleep(0.005)

    # Arduinoからデータを受け取る
    # def receiveloop(self):
    #     while True:
    #         line = self.ser.readline().decode("utf-8").rstrip()
    #         self.data_parts = line.split(",")
    #         self.bendingValue = self.data_parts[0].rstrip()
    #         print(self.data_parts)
    #         time.sleep(0.005)


if __name__ == "__main__":
    text_class = Text_class()
    time.sleep(0.5)
    while True:
        try:
            time.sleep(0.005)
        except KeyboardInterrupt:
            print("KeyboardInterrupt Stop:text")
            break
