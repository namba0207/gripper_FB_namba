# Arduino_gripper_out.inoとセット！！,押し込み表現拡大，ロボtグリッパー掴みから100まで
import csv
import random
import threading
import time
from random import randint

import numpy as np

# import numpy as np
import serial
from ArmWrapper1000 import ArmWrapper
from pynput import keyboard, mouse
from scipy import stats as st
from xarm.wrapper import XArmAPI


class Text_class:
    def __init__(self):
        self.x_data = np.array([])
        self.x_data = np.array([])
        self.x_list = np.array([])
        self.y_list = np.array([])
        self.slope_h = 0
        self.grippos = 0
        self.flag = 0
        self.sample_list = [1, 2, 4]
        ip = "192.168.1.199"
        self.ser = serial.Serial("COM8", 115200)
        not_used = self.ser.readline()
        self.ser2 = serial.Serial("COM7", 115200)
        self.not_used = self.ser2.readline()
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

        thr0 = threading.Thread(target=self.sendloop)
        thr0.setDaemon(True)
        thr0.start()
        thr1 = threading.Thread(target=self.receiveloop)
        thr1.setDaemon(True)
        thr1.start()

    def press(self, key):
        print("アルファベット {0} が押されました".format(key.char))
        if format(key.char) == "r":
            self.num1 = randint(1, 2)
            self.num2 = randint(1, 2)
            self.num3 = randint(1, 2)
            self.numlist = random.sample(self.sample_list, 3)
            # print(self.num1, self.num2, self.num3, self.numlist)
            with open("data0201chikao4.csv", "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        self.num1,
                        self.num2,
                        self.num3,
                        self.numlist,
                    ]
                )

    def sendloop(self):
        slope = 0
        while True:
            # 掴み始め・離し始め
            if self.flag == 0 and self.datal.loadcell_int >= 130:
                self.grip = self.arm.get_gripper_position()[1]
                self.flag = 1
            elif self.datal.loadcell_int < 130:
                self.grip = 0
                self.flag = 0
            if self.flag == 0:
                self.x_list = np.array([])
                self.y_list = np.array([])
                self.slope_h = 0
            else:
                self.pos2 = int(
                    (self.grip - self.arm.get_gripper_position()[1])
                    * (255 - 0)
                    / (280 - 200)  # 止まるところでグリッパー閉じ切る
                )
                self.x_list = np.append(
                    self.x_list, [self.grip - self.arm.get_gripper_position()[1]]
                )
                self.y_list = np.append(self.y_list, [self.datal.loadcell_int - 129])
                # データ数が10を超えたら古いデータを削除!!!最初の数字を(0,0)にしないと最小二乗法ですべての点が同じ時に傾きがぶれやすくなる！！
                if len(self.x_list) > 10:
                    self.x_list = self.x_list[2:]
                    self.y_list = self.y_list[2:]
                    self.x_list = np.insert(self.x_list, 0, 0)
                    self.y_list = np.insert(self.y_list, 0, 0)
                if len(self.x_list) >= 10:
                    self.x_data = np.array([self.x_list])
                    self.y_data = np.array([self.y_list])
                    if np.std(self.x_data) == 0:
                        pass
                    else:
                        slope, intercept, r_value, p_value, std_err = st.linregress(
                            self.x_data[-1:-11:-1], self.y_data[-1:-11:-1]
                        )
                    print("傾き:{0}".format(slope))
                    if slope < 0.1:
                        pass
                    elif slope < 0.5:
                        slope = 0.5
                    elif slope > 2.5:
                        slope = 2.5
                    slope = 1 / slope
                    self.slope_h = int((slope - 1 / 2.5) * (255 - 0))
                    if self.slope_h > 150:
                        self.slope_h = 150
                    elif self.slope_h < 0:
                        self.slope_h = 0
                    # print(self.slope_h)
            self.ser2.write(bytes([self.slope_h]))
            self.pos1_str = str(self.datal.loadcell_int) + "\n"
            self.ser.write(self.pos1_str.encode())
            time.sleep(0.0005)

    def receiveloop(self):
        """
        Receiving data from bending sensor and update self.bendingValue
        """
        try:
            self.pretime = time.perf_counter()
            while True:
                self.line = self.ser.readline().decode("utf-8").rstrip()
                self.data_parts = self.line.split(",")
                self.bendingValue_int = int(
                    400
                    - int(self.data_parts[0].rstrip())
                    / 2200
                    * 400  # 発振するときデバイスの可動域の大きさ注意！!
                )
                if self.bendingValue_int > 400:
                    self.bendingValue_int = 400
                elif self.bendingValue_int < 200:
                    self.bendingValue_int = 200
                self.bendingValue = self.bendingValue_int
                code, ret = self.arm.getset_tgpio_modbus_data(
                    self.datal.ConvertToModbusData(self.bendingValue)
                )
                # time.sleep((0.00005))
                print(self.slope_h)
        except KeyboardInterrupt:
            print("KeyboardInterrupt >> Stop: BendingSensorManager.py")


if __name__ == "__main__":
    text_class = Text_class()
    listener = keyboard.Listener(on_press=text_class.press)
    listener.start()
    while True:
        try:
            # pass
            time.sleep(0.01)
        except KeyboardInterrupt:
            print("KeyboardInterrupt Stop:text")
            break
