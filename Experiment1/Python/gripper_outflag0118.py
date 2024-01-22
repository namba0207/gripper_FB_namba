# Arduino_gripper_out.inoとセット！！,押し込み表現拡大，ロボtグリッパー掴みから100まで
# import csv
import math
import threading
import time
from pynput import mouse, keyboard
# import sys
import random
from random import randint
# import numpy as np
import serial
from ArmWrapper1000 import ArmWrapper
from xarm.wrapper import XArmAPI


class Text_class:
    def __init__(self):
        self.oshikomi = []
        self.speed = []
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
        
    def press(self,key):
        try:
            print('アルファベット {0} が押されました'.format(key.char))
            if format(key.char) == '0':
                self.num1 = randint(1, 2)
                self.num2 = randint(1, 2)
                self.num3 = randint(1, 2)
                self.numlist = random.sample(self.sample_list, 3)
                print(self.num1,self.num2,self.num3,self.numlist)
                j = 0
                
                while j < 3:
                    if self.numlist[j] == 1:
                        self.oshikomi += [random.choice((160, 220))]
                    if self.numlist[j] == 2:
                        self.oshikomi += [random.choice((180, 230))]
                    if self.numlist[j] == 4:
                        self.oshikomi += [random.choice((200, 240))]
                    j += 1
                self.speed = [
                    random.choice((0.5, 1, 2)),
                    random.choice((0.5, 1, 2)),
                    random.choice((0.5, 1, 2)),
                ]
                k = 0
                while k < 3:
                    print("self.oshikomi" + str(k) + ", self.speed"+ str(k) +" = "+ str(self.oshikomi[k])+ ","+ str(self.speed[k]))
                    k += 1
                
            if format(key.char) == '1':
                thr1 = threading.Thread(target=self.moveloop)
                thr1.setDaemon(True)
                thr1.start()
            
        except AttributeError:
            print('スペシャルキー {0} が押されました'.format(key))

    def release(self,key):
        if key == keyboard.Key.esc:     # escが押された場合
            return False    # listenerを止める
        
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
                    / (self.grippos - 175)  # 止まるところでグリッパー閉じ切る
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
        while i<3:
            self.start_time = time.perf_counter()
            while self.data1 < 5:
                self.data1 = time.perf_counter() - self.start_time
                if self.data1 < 2:
                    self.data2 = 400 - (400 - self.oshikomi[i]) / (
                        1 + self.e ** -(self.data1 * self.speed[i] * 20 - 10)
                    )
                elif self.data1 < 4:
                    self.data2 = 400 - (400 - self.oshikomi[i]) / (
                        1 + self.e ** (self.data1 * self.speed[i] * 20 - 30)
                    )
                else:
                    self.data2 = 400
                code, ret = self.arm.getset_tgpio_modbus_data(
                    self.datal.ConvertToModbusData(self.data2)
                )
                time.sleep(0.005)
            i+=1
            print(i)
        print("mooveloop_finish")
    
if __name__ == "__main__":
    text_class = Text_class()
    listener = keyboard.Listener(
        on_press=text_class.press,
        on_release=text_class.release)
    listener.start()
    time.sleep(2)
    while True:
        try:
            pass
            # text_class.line = text_class.ser.readline().decode("utf-8").rstrip()
            # print(
            #     # 2200 - int(self.arm.get_gripper_position()[1] / 400 * 2200),
            #     text_class.datal.loadcell_int,
            #     int(text_class.arm.get_gripper_position()[1]),
            #     text_class.line,
            # )
            # time.sleep(0.01)
        except KeyboardInterrupt:
            print("KeyboardInterrupt Stop:text")
            break
