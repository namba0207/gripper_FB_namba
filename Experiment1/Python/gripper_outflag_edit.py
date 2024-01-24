# Arduino_gripper_out.inoとセット！！,押し込み表現拡大，ロボtグリッパー掴みから100まで
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


class Text_class:
    def __init__(self):
        self.recode_list = [0,0,0,0,0,0]
        self.data1 = 0
        self.oshikomi = [200, 200, 200]
        self.oshikomi_rec = [200,200,200]
        self.speed = [1, 1, 1]
        self.sample_list = [1, 2, 4]
        self.data2 = 400
        self.num = 0
        self.grippos = 0
        self.flag = 0
        self.e = math.e
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
                        self.oshikomi[j] = random.choice((185, 220))  # 200-230
                    if self.numlist[j] == 2:
                        self.oshikomi[j] = random.choice((190, 230))  # 210-240
                    if self.numlist[j] == 4:
                        self.oshikomi[j] = random.choice((200, 240))  # 220-250
                    self.speed[j] = random.choice((1, 2, 3))
                    if self.oshikomi[j] == 185:
                        self.oshikomi_rec[j] = 200
                    elif self.oshikomi[j] == 190:
                        self.oshikomi_rec[j] = 210
                    elif self.oshikomi[j] == 200:
                        self.oshikomi_rec[j] = 220
                    else:
                        self.oshikomi_rec[j] += self.oshikomi[j] + 10
                    self.recode_list[2*j] = self.oshikomi_rec[j]
                    self.recode_list[2*j+1] = self.speed[j]
                    j += 1
                with open("data0123_3.csv", "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([self.num1, self.num2, self.num3,self.numlist, self.recode_list])
                

            if format(key.char) == "s":
                print("thread_start")
                thr1 = threading.Thread(target=self.moveloop)
                thr1.setDaemon(True)
                thr1.start()

        except AttributeError:
            pass

    # グリッパーの値をArduinoへ送る
    def sendloop(self):
        while True:
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
                    / (self.grippos - 200)  # 止まるところでグリッパー閉じ切る
                )
            if self.num > 255:
                self.num = 255
            elif self.num < 0:
                self.num = 0
            # self.ser.write(bytes([self.num]))
            self.num_str = str(self.num + 100) + "\n"  # 100-355
            self.ser.write(self.num_str.encode())
            time.sleep(0.01)

    def moveloop(self):
        i = 0
        while i < 3:
            self.start_time = time.perf_counter()
            while self.data1 < 5:
                self.data1 = time.perf_counter() - self.start_time
                if self.data1 < 2:
                    self.data2 = 400 - (400 - self.oshikomi[i]) / (
                        1 + self.e ** -(self.data1 * self.speed[i] * 10 - 10)
                    )
                elif self.data1 < 4:
                    self.data2 = 400 - (400 - self.oshikomi[i]) / (
                        1 + self.e ** (self.data1 * self.speed[i] * 10 - 30)
                    )
                else:
                    self.data2 = 400
                code, ret = self.arm.getset_tgpio_modbus_data(
                    self.datal.ConvertToModbusData(self.data2)
                )
                # print(self.data1, self.data2)
                print(
                    int(self.arm.get_gripper_position()[1]),
                    self.datal.loadcell_int,
                )
                time.sleep(0.005)
            self.data1 = 0
            i += 1
            print(i)
        print("mooveloop_finish")


if __name__ == "__main__":
    text_class = Text_class()
    listener = keyboard.Listener(on_press=text_class.press)
    listener.start()
    print("rでランダム決める")
    while True:
        try:
            # pass
            time.sleep(0.01)
        except KeyboardInterrupt:
            print("KeyboardInterrupt Stop:text")
            break
