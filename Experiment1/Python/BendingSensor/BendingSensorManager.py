# -----------------------------------------------------------------------
# Author:   Takumi Katagiri (Nagoya Institute of Technology), Takayoshi Hagiwara (KMD)
# Created:  2021
# Summary:  曲げセンサからのデータ取得用マネージャー
# -----------------------------------------------------------------------

import threading

# import socket
import time

import numpy as np
import RobotArmController.Robotconfig as RC
import RobotArmController.Robotconfig_pos as RP
import RobotArmController.Robotconfig_vib as RV
import serial


class BendingSensorManager:
    def __init__(self, ip, port) -> None:
        self.ip = ip
        self.port = port
        self.bendingValue = 850
        self.bendingValue_sub = 0
        self.ser = serial.Serial(ip, port)
        self.not_used = self.ser.readline()
        # self.num = 127

    def thread(self):
        while True:
            # if RC.num_int > 255:
            #     self.num = 255
            # elif RC.num_int < 0:
            #     self.num = 0
            self.ser.write(bytes([RC.num_int]))
            # print(RC.num_int)
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
                    850
                    - int(self.data_parts[0].rstrip())
                    / 2000
                    * 850  # 発振するときデバイスの可動域の大きさ注意！!
                )
                if self.bendingValue_int > 850:
                    self.bendingValue_int = 850
                elif self.bendingValue_int < 0:
                    self.bendingValue_int = 0
                self.bendingValue = self.bendingValue_int
                self.bendingVelocity = (
                    int(self.data_parts[1].rstrip()) - self.bendingValue_sub
                ) / (time.perf_counter() - self.pretime)
                RV.num_v = self.bendingVelocity
                self.pretime = time.perf_counter()
                self.bendingValue_sub = int(self.data_parts[1].rstrip())
                print(self.data_parts, RC.num_int)
        except KeyboardInterrupt:
            print("KeyboardInterrupt >> Stop: BendingSensorManager.py")
