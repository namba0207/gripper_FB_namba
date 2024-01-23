# -----------------------------------------------------------------------
# Author:   Takumi Katagiri (Nagoya Institute of Technology), Takayoshi Hagiwara (KMD)
# Created:  2021
# Summary:  曲げセンサからのデータ取得用マネージャー
# -----------------------------------------------------------------------

import threading
import time

import numpy as np
import RobotArmController.Robotconfig as RC
import RobotArmController.Robotconfig_pos as RP
import RobotArmController.Robotconfig_vib as RV
import serial
from xarm.wrapper import XArmAPI


class BendingSensorManager:
    def __init__(self, ip, port) -> None:
        self.flag = 0
        self.ip = ip
        self.port = port
        self.bendingValue = 400
        self.bendingValue_sub = 0
        self.ser = serial.Serial(ip, port)
        self.not_used = self.ser.readline()
        self.arm = XArmAPI("192.168.1.199")

    def thread(self):
        while True:
            # 掴み始め・離し始め
            if self.flag == 0 and RC.num_int >= 129:
                self.grip = self.arm.get_gripper_position()[1]
                self.flag = 1
            elif RC.num_int < 129:
                self.grip = 0
                self.flag = 0
            if self.flag == 0:
                self.pos2 = int(0)
            else:
                self.pos2 = int(
                    (self.grip - self.arm.get_gripper_position()[1])
                    * (255 - 0)
                    / (self.grip - 200)  # 止まるところでグリッパー閉じ切る
                )
            if self.pos2 > 255:
                self.pos2 = 255
            elif self.pos2 < 0:
                self.pos2 = 0
            self.num_str = str(RC.num_int) + "," + str(self.pos2) + "\n"
            self.ser.write(self.num_str.encode())
            # self.ser.write(bytes([RC.num_int]))
            time.sleep(0.0005)

    def StartReceiving(self):
        """
        Receiving data from bending sensor and update self.bendingValue
        """
        try:
            thr = threading.Thread(target=self.thread)
            thr.setDaemon(True)
            thr.start()
            self.pretime = time.perf_counter()
            while True:
                line = self.ser.readline().decode("utf-8").rstrip()
                self.data_parts = line.split(",")
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
                self.bendingVelocity = (
                    int(self.data_parts[1].rstrip()) - self.bendingValue_sub
                ) / (time.perf_counter() - self.pretime)
                RV.num_v = self.bendingVelocity
                self.pretime = time.perf_counter()
                self.bendingValue_sub = int(self.data_parts[1].rstrip())
                # print(self.data_parts, RC.num_int, self.arm.get_gripper_position()[1])
        except KeyboardInterrupt:
            print("KeyboardInterrupt >> Stop: BendingSensorManager.py")
