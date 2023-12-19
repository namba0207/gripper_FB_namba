# 反力そのままフィードバック
import csv  # 記録用
import os
import signal
import sys
import threading
import time

import numpy as np
import serial

# ip = '192.168.1.240'
ip = "192.168.1.199"

# data_record = []  # 記録用

arduino_port = "COM8"
baud_rate = 115200
ser = serial.Serial(arduino_port, baud_rate)
not_used = ser.readline()

sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from xarm.wrapper import XArmAPI

arm = XArmAPI(ip)
time.sleep(0.5)
if arm.warn_code != 0:
    arm.clean_warn()
if arm.error_code != 0:
    arm.clean_error()

arm.motion_enable(True)
arm.set_mode(0)
arm.set_state(0)
# ーーーーーーーーーーーーーーーーーーーーーーーーーーーーmainーーーーーーーーーーーーーーーーーーーーーーーーーー
from ArmWrapper1000 import ArmWrapper

datal = ArmWrapper(True, ip)
global num_str
global pos
num_str = str(127)
pos = str(500)


def thread():
    startTime = time.perf_counter()
    while True:
        # code3//ESP32からencoder受信(loadcell受信)
        line = ser.readline().decode("utf-8").rstrip()
        # データの抽出と変数への代入
        # data_parts = line.split(",")
        # pos1 = int(850 - float(data_parts[0]) / 1600 * 850)  # -425-0
        # pos2 = int(425+float(data_parts[1])/1400*850/2)#-425-0
        # pos2 = 0
        # pos3 = int(float(data_parts[2]))  # -425-0
        # pos4 = int(float(data_parts[3]))  # -425-0
        # pos1 = int(212.5 * (np.sin(2 * np.pi * 0.3 * (time.perf_counter()-startTime)) + 1))
        pos1 = 500 - 100 * (time.perf_counter() - startTime)
        if (time.perf_counter() - startTime) > 5:
            pos1 = 0
        if (time.perf_counter() - startTime) > 10:
            pos1 = 0 + 100 * (time.perf_counter() - startTime - 10)
        # data_record.append([pos1, num_str, time.perf_counter()])  # 記録用
        pos_gripper = pos1
        if pos_gripper > 850:
            pos_gripper = 850
        elif pos_gripper < 0:
            pos_gripper = 0
        pos = str(pos1)
        print(pos_gripper, pos1, int(num_str))
        # code4//encoderの値をgripperへ送信
        code, ret = arm.getset_tgpio_modbus_data(datal.ConvertToModbusData(pos_gripper))


try:
    # startTime = time.perf_counter()
    thr = threading.Thread(target=thread)
    thr.setDaemon(True)  # threadをDaemonにすることでmain文終了で自動で終了する
    thr.start()
    # code5//loadcell読み取り
    while True:
        num = int(datal.loadcell_val * 1000)
        if num > 150:
            num = 150
        elif num < 0:
            num = 0
        num_int = int(num / 150 * (220 - 127) + 127)
        num_str = str(num_int)
        # code6//loadcell送信
        ser.write(bytes([num_int]))
        with open("data.txt", mode="a") as txt_file:
            txt_file.write(
                pos + "  " + num_str + "  " + str(time.perf_counter()) + "\n"
            )
        # print(time.perf_counter(), num_str)
        time.sleep(0.02)  # ターミナルで大きさ変更0.03が遅延なくできる
except KeyboardInterrupt:
    print("except KeyboardInterrupt")
    # with open("data_record/" + "data1", "w", newline="") as f:
    # writer = csv.writer(f)
    # writer.writerow(['pos1', 'pos2', 'loadcell'])
    # writer.writerows(data_record)
    ser.close()
    sys.exit()
# # python gripper_con1108.py
# # env\Scripts\Activate.ps1
