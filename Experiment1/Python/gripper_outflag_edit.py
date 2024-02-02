# Arduino_gripper_out.inoとセット！！,押し込み表現拡大，ロボtグリッパー掴みから100まで
import csv
import math
import random
import threading
import time
from random import randint

import numpy as np
import serial
from ArmWrapper1000 import ArmWrapper
from pynput import keyboard, mouse

# 最小二乗法
from scipy import stats as st
from xarm.wrapper import XArmAPI


class Text_class:
    def __init__(self):
        self.recode_list = [0, 0, 0, 0, 0, 0]
        self.data1 = 0
        self.oshikomi = [185, 190, 200]
        self.oshikomi = [220, 230, 240]
        self.oshikomi_rec = [200, 200, 200]
        self.speed = [1, 1, 1]
        self.sample_list = [1, 2, 4]
        self.data2 = 400
        self.num = 0
        self.grippos = 0
        self.flag = 0
        self.e = math.e
        self.x_list = np.array([])
        self.y_list = np.array([])
        self.slope_h = 0
        ip = "192.168.1.199"
        print("シリアル通信開始予定")
        self.ser1 = serial.Serial("COM8", 115200)
        self.ser2 = serial.Serial("COM7", 115200)
        not_used1 = self.ser1.readline()
        not_used2 = self.ser2.readline()
        print("シリアル通信開始完了")
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

    def press(self, key):
        try:
            # print("アルファベット {0} が押されました".format(key.char))
            if format(key.char) == "r":
                self.num1 = randint(1, 2)
                self.num2 = randint(1, 2)
                self.num3 = randint(1, 2)
                self.numlist = random.sample(self.sample_list, 3)
                # print(self.num1, self.num2, self.num3, self.numlist)
                print("保存データの確認、スタートはs,ミスしたら再起動")
                j = 0
                while j < 3:
                    if self.numlist[j] == 1:
                        self.oshikomi[j] = random.choice((188, 220))  # 200-230
                    if self.numlist[j] == 2:
                        self.oshikomi[j] = random.choice((193, 230))  # 210-240
                    if self.numlist[j] == 4:
                        self.oshikomi[j] = random.choice((200, 240))  # 220-250
                    self.speed[j] = random.choice((10, 20, 30))
                    if self.oshikomi[j] == 188:
                        self.oshikomi_rec[j] = 200
                    elif self.oshikomi[j] == 193:
                        self.oshikomi_rec[j] = 210
                    elif self.oshikomi[j] == 200:
                        self.oshikomi_rec[j] = 220
                    else:
                        self.oshikomi_rec[j] = self.oshikomi[j] + 10
                    self.recode_list[2 * j] = self.oshikomi_rec[j]
                    self.recode_list[2 * j + 1] = self.speed[j]
                    j += 1
                # print(self.oshikomi, self.oshikomi_rec)
                with open("data0201.csv", "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        [
                            self.num1,
                            self.num2,
                            self.num3,
                            self.numlist,
                            self.recode_list,
                        ]
                    )

            if format(key.char) == "s":
                print("thread_start")
                thr1 = threading.Thread(target=self.moveloop)
                thr1.setDaemon(True)
                thr1.start()

        except AttributeError:
            pass

    # グリッパーの値をArduinoへ送る
    def sendloop(self):
        slope = 0
        self.x_data = np.array([0])
        self.x_data = np.array([0])
        while True:
            # 掴み始め・離し始め
            if self.flag == 0 and self.datal.loadcell_int >= 129:
                self.grippos = self.arm.get_gripper_position()[1]
                self.flag = 1
            elif self.datal.loadcell_int < 129:
                self.grippos = 0
                self.flag = 0
            if self.flag == 0:
                self.x_list = np.array([0])
                self.y_list = np.array([0])
                self.slope_h = 0
                # print("hello")
            else:
                self.x_list = np.append(
                    self.x_list, [self.grippos - self.arm.get_gripper_position()[1]]
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
                    if slope < 0.2 or slope > 2.5:
                        slope = 2.5
                    slope = 1 / slope
                    self.slope_h = int((slope - 1 / 2.5) * (255 - 0))
                    if self.slope_h > 150:
                        self.slope_h = 150
                    elif self.slope_h < 0:
                        self.slope_h = 0
            self.num_str = str(self.num + 100) + "\n"  # 100-355
            self.ser1.write(self.num_str.encode())
            self.ser2.write(bytes([self.slope_h]))
            # print(self.slope_h)
            # print(self.x_list, self.y_list)
            # print(
            #     self.grippos,
            #     self.arm.get_gripper_position()[1],
            #     self.datal.loadcell_int,
            # )
            time.sleep(0.01)

    def moveloop(self):
        i = 0
        while i < 3:
            self.start_time = time.perf_counter()
            while self.data1 < 5:
                self.data1 = time.perf_counter() - self.start_time
                if self.data1 < 2:
                    self.data2 = (400 - self.oshikomi[i]) / (
                        1 + self.e ** (self.data1 * self.speed[i] - 10)
                    ) + self.oshikomi[i]
                elif self.data1 < 4:
                    self.data2 = (400 - self.oshikomi[i]) / (
                        1 + self.e ** -((self.data1 - 2) * self.speed[i] - 10)
                    ) + self.oshikomi[i]
                else:
                    self.data2 = 400
                code, ret = self.arm.getset_tgpio_modbus_data(
                    self.datal.ConvertToModbusData(self.data2)
                )
                # print(self.data1, self.data2)

                time.sleep(0.01)
            self.data1 = 0
            i += 1
            print(i)
        print("movefinish")
        self.finish_time = 0
        self.start_time = time.perf_counter()
        while self.finish_time < 10:
            self.finish_time = time.perf_counter() - self.start_time
            print(self.finish_time)
            time.sleep(1)
        print("moveloopfinish")


if __name__ == "__main__":
    text_class = Text_class()
    listener = keyboard.Listener(on_press=text_class.press)
    listener.start()
    print("rでランダム決める")
    while True:
        try:
            # print(111)
            time.sleep(0.01)
        except KeyboardInterrupt:
            print("KeyboardInterrupt Stop:text")
            break
