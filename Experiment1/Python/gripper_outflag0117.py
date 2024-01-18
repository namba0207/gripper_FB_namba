# Arduino_gripper_out.inoとセット！！,押し込み表現拡大，ロボtグリッパー掴みから100まで
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
        self.num = 0
        self.grippos = 0
        self.flag = 0
        
        ip = "192.168.1.199"
        arduino_port = "COM8"
        baud_rate = 115200
        self.ser = serial.Serial(arduino_port, baud_rate)
        not_used = self.ser.readline()
        self.arm = XArmAPI(ip)
        self.datal = ArmWrapper(True, ip)
        self.datal.loadcell_int = 127
        time.sleep(0.5)
        if self.arm.warn_code != 0:
            self.arm.clean_warn()
        if self.arm.error_code != 0:
            self.arm.clean_error()
        self.arm.motion_enable(True)
        self.arm.set_mode(0)
        self.arm.set_state(0)

        # thr1 = threading.Thread(target=self.loadcellloop)
        # thr1.setDaemon(True)
        # thr1.start()
        thr2 = threading.Thread(target=self.sendloop)
        thr2.setDaemon(True)
        thr2.start()
        thr3 = threading.Thread(target=self.moveloop)
        thr3.setDaemon(True)
        thr3.start()

    # def loadcellloop(self):
    #     self.init_loadcell_val = self.arm.get_cgpio_analog(1)[1]
    #     while True:
    #         self.loadcell = (
    #             float(self.arm.get_cgpio_analog(1)[1]) - float(self.init_loadcell_val)
    #         ) * 1000
    #         if self.loadcell > 200:
    #             self.loadcell = 200
    #         elif self.loadcell < 0:
    #             self.loadcell = 0
    #         self.datal.loadcell_int = int(self.loadcell / (200 - 0) * (255 - 127) + 127)
    #         time.sleep(0.001)

    # グリッパーの値をArduinoへ送る
    def sendloop(self):
        with open(
            # "C:\\Users\\SANOLAB\\Documents\\GitHub\\gripper_FB_namba\\cul10_100.csv"
            # "C:\\Users\\SANOLAB\\Documents\\GitHub\\gripper_FB_namba\\cul10_150.csv"
            # "C:\\Users\\SANOLAB\\Documents\\GitHub\\gripper_FB_namba\\cul10_200.csv"
            # "C:\\Users\\SANOLAB\\Documents\\GitHub\\gripper_FB_namba\\cul20_100.csv"
            # "C:\\Users\\SANOLAB\\Documents\\GitHub\\gripper_FB_namba\\cul20_150.csv"
            # "C:\\Users\\SANOLAB\\Documents\\GitHub\\gripper_FB_namba\\cul20_200.csv"
            # "C:\\Users\\SANOLAB\\Documents\\GitHub\\gripper_FB_namba\\cul40_100.csv"
            # "C:\\Users\\SANOLAB\\Documents\\GitHub\\gripper_FB_namba\\cul40_150.csv"  # 中間、硬いが力同じ位置ほぼ同じ
            "C:\\Users\\SANOLAB\\Documents\\GitHub\\gripper_FB_namba\\cul40_200.csv" 
        ) as f1:
            reader = csv.reader(f1)
            self.l1 = [row for row in reader]
        self.count = 0
        while True:
            self.bendingValue_int = int(float(self.l1[self.count][1]))
            if self.bendingValue_int > 400:
                self.bendingValue_int = 400
            elif self.bendingValue_int < 0:
                self.bendingValue_int = 0
            # 掴み始め・離し始め
            if self.flag == 0 and self.datal.loadcell_int >= 129:
                self.grippos = self.arm.get_gripper_position()[1]
                self.flag = 1
            elif self.datal.loadcell_int < 129:
                self.grippos = 0
                self.flag = 0
            if self.flag == 0:
                self.num = int(0)
            else:
                self.num = int(
                    (self.grippos - self.arm.get_gripper_position()[1])
                    * (255 - 0)
                    / (self.grippos - 100)  # 止まるところでグリッパー閉じ切る
                )
            if self.num > 255:
                self.num = 255
            elif self.num < 0:
                self.num = 0
            self.ser.write(bytes([self.num]))
            # print(self.bendingValue_int, self.num)
            self.count += 1
            time.sleep(0.01)

    def moveloop(self):
        while True:
            code, ret = self.arm.getset_tgpio_modbus_data(
                self.datal.ConvertToModbusData(self.bendingValue_int)
            )
            time.sleep(0.005)


if __name__ == "__main__":
    text_class = Text_class()
    while True:
        try:
            text_class.line = text_class.ser.readline().decode("utf-8").rstrip()
            print(
                # 2200 - int(self.arm.get_gripper_position()[1] / 400 * 2200),
                # text_class.datal.loadcell_int,
                int(text_class.arm.get_gripper_position()[1]),
                text_class.line,
            )
            # time.sleep(0.01)
        except KeyboardInterrupt:
            print("KeyboardInterrupt Stop:text")
            break
