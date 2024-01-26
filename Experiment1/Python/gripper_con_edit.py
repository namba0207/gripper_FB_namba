# Arduino_gripper_out.inoとセット！！,押し込み表現拡大，ロボtグリッパー掴みから100まで
import csv
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
        self.grippos = 0
        self.flag = 0
        self.sample_list = [1, 2, 4]
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
            with open("data0126_kaiyu2.csv", "a", newline="") as file:
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
        while True:
            # 掴み始め・離し始め
            if self.flag == 0 and self.datal.loadcell_int >= 129:
                self.grippos = self.arm.get_gripper_position()[1]
                self.flag = 1
            elif self.datal.loadcell_int < 129:
                self.grippos = 0
                self.flag = 0
            if self.flag == 0:
                self.pos2 = int(0)
            else:
                self.pos2 = int(
                    (self.grippos - self.arm.get_gripper_position()[1])
                    * (255 - 0)
                    / (self.grippos - 200)  # 止まるところでグリッパー閉じ切る
                )
            if self.pos2 > 255:
                self.pos2 = 255
            elif self.pos2 < 0:
                self.pos2 = 0
            self.pos1_str = str(self.datal.loadcell_int) + "," + str(self.pos2) + "\n"
            self.ser.write(self.pos1_str.encode())
            # self.ser.write(bytes([RC.pos1_int]))
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
                elif self.bendingValue_int < 0:
                    self.bendingValue_int = 0
                self.bendingValue = self.bendingValue_int
                code, ret = self.arm.getset_tgpio_modbus_data(
                    self.datal.ConvertToModbusData(self.bendingValue)
                )
                print(self.line)
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
