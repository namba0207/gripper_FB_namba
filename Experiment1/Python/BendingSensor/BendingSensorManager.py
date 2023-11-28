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
import serial


class BendingSensorManager:
    def __init__(self, ip, port) -> None:
        self.ip = ip
        self.port = port
        self.bendingValue = 850
        self.ser = serial.Serial(ip, port)
        self.not_used = self.ser.readline()

    def thread(self):
        while True:
            self.ser.write(bytes([RC.num_int]))
            time.sleep(0.03)

    def StartReceiving(self):
        """
        Receiving data from bending sensor and update self.bendingValue
        """
        try:
            thr = threading.Thread(target=self.thread)
            thr.setDaemon(True)
            thr.start()
            while True:
                # code3//ESP32からencoder受信(loadcell受信)
                line = self.ser.readline().decode("utf-8").rstrip()
                # データの抽出と変数への代入
                data_parts = line.split(",")
                self.bendingValue_int = int(
                    850 - int(data_parts[0].rstrip()) / 1500 * 850
                )  # -425-0
                if self.bendingValue_int > 850:
                    self.bendingValue_int = 850
                elif self.bendingValue_int < 0:
                    self.bendingValue_int = 0
                self.bendingValue = self.bendingValue_int
                print(RC.num_int, data_parts)
        except KeyboardInterrupt:
            print("KeyboardInterrupt >> Stop: BendingSensorManager.py")
