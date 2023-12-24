# 反力そのままフィードバック
import csv  # 記録用
import os
import signal
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
        startTime = time.perf_counter()
        while True:
            # code3//ESP32からencoder受信(loadcell受信)
            line = self.ser.readline().decode("utf-8").rstrip()
            self.data_parts = line.split(",")
            self.pos1 = 500 - 100 * (time.perf_counter() - startTime)
            if (time.perf_counter() - startTime) > 2.5:
                self.pos1 = 250
            if (time.perf_counter() - startTime) > 5:
                self.pos1 = 250 + 100 * (time.perf_counter() - startTime - 5)
            # data_record.append([pos1, num_str, time.perf_counter()])  # 記録用
            self.pos_gripper = self.pos1
            if self.pos_gripper > 850:
                self.pos_gripper = 850
            elif self.pos_gripper < 0:
                self.pos_gripper = 0
            # code4//encoderの値をgripperへ送信
            code, ret = self.arm.getset_tgpio_modbus_data(
                self.datal.ConvertToModbusData(self.pos_gripper)
            )
            self.pos = self.arm.get_gripper_position()[1]
            # print(self.pos)

    def loop(self):
        try:
            # code5//loadcell読み取り
            while True:
                self.num = int(self.datal.loadcell_val * 1000)
                if self.num > 250:
                    self.num = 250
                elif self.num < 0:
                    self.num = 0
                self.num_int = int(self.num / (250 - 0) * (255 - 127) + 127)
                # code6//loadcell送信
                self.ser.write(bytes([self.num_int]))
                time.sleep(0.005)
        except KeyboardInterrupt:
            print("except KeyboardInterrupt")
            self.ser.close()
            sys.exit()


if __name__ == "__main__":
    text_class = Text_class()
    time.sleep(0.5)
    while True:
        try:
            with open("data.txt", mode="a") as txt_file:
                txt_file.write(
                    str(text_class.pos)
                    + " "
                    + str(text_class.num_int)
                    + " "
                    + str(text_class.data_parts[2])
                    + " "
                    + str(time.perf_counter())
                    + "\n"
                )
            print(
                text_class.pos,
                text_class.num_int,
                text_class.data_parts[2],
                time.perf_counter(),
            )
            time.sleep(0.005)
        except KeyboardInterrupt:
            print("KeyboardInterrupt Stop:text")
            break
