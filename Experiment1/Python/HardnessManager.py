# M5stackとセット#2個同時にシリアル通信
import csv
import math

# import sys
import random
import threading
import time
from random import randint

# import numpy as np
import serial
from ArmWrapper1000 import ArmWrapper
from pynput import keyboard, mouse
from xarm.wrapper import XArmAPI

ser1 = serial.Serial("COM7", 115200)
ser2 = serial.Serial("COM8", 115200)

while True:
    try:
        ser1.write(bytes([118]))
        ser2.write(bytes([117]))
        line1 = ser1.readline().decode("utf-8").rstrip()
        line2 = ser2.readline().decode("utf-8").rstrip()
        print(line1, line2)
        time.sleep(0.001)
    except KeyboardInterrupt:
        print("finish")
        break

# class Hardness_class:
#     def __init__(self):

# self.num = 0
# self.grippos = 0
# self.flag = 0
# ip = "192.168.1.199"
#         self.arm = XArmAPI(ip)
#         self.datal = ArmWrapper(True, ip)
#         self.datal.loadcell_int = 127
#         time.sleep(0.5)
#         if self.arm.warn_code != 0:
#             self.arm.clean_warn()
#         if self.arm.error_code != 0:
#             self.arm.clean_error()
#         self.arm.motion_enable(True)
#         self.arm.set_mode(0)
#         self.arm.set_state(0)

#         thr0 = threading.Thread(target=self.sendloop)
#         thr0.setDaemon(True)
#         thr0.start()

#     # グリッパーの値をArduinoへ送る
#     def sendloop(self):
#         while True:
#             # 掴み始め・離し始め
#             if self.flag == 0 and self.datal.loadcell_int >= 129:
#                 self.grippos = self.arm.get_gripper_position()[1]
#                 self.flag = 1
#             elif self.datal.loadcell_int < 129:
#                 self.grippos = 0
#                 self.flag = 0
#             if self.flag == 0:
#                 self.num = int(0)
#             else:
#                 self.num = int(255)
#             if self.num > 255:
#                 self.num = 255
#             elif self.num < 0:
#                 self.num = 0
#             self.ser.write(bytes([self.num]))
#             time.sleep(0.01)


# if __name__ == "__main__":
#     hard_class = Hardness_class()
#     while True:
#         try:
#             # pass
#             time.sleep(0.01)
#         except KeyboardInterrupt:
#             print("KeyboardInterrupt Stop:text")
#             break
