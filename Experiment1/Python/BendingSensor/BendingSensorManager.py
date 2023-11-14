# -----------------------------------------------------------------------
# Author:   Takumi Katagiri (Nagoya Institute of Technology), Takayoshi Hagiwara (KMD)
# Created:  2021
# Summary:  曲げセンサからのデータ取得用マネージャー
# -----------------------------------------------------------------------

# import socket
import time

import numpy as np
import serial

# from UDP.UDPManager import UDPManager


class BendingSensorManager:
    def __init__(self, ip, port) -> None:
        self.ip = ip
        self.port = port
        # self.bufsize = 4096
        self.bendingValue = 850

        # wireless
        # self.udpManager = UDPManager(port=self.port, localAddr=self.ip)

        # serial
        # self.serialObject = serial.Serial(ip, port)
        # nonUsed = self.serialObject.readline()
        self.ser = serial.Serial(ip, port)
        self.not_used = self.ser.readline()

        """
        self.ser1 = serial.Serial("COM3",9600)
        self.not_used1 = self.ser1.readline()
        self.ser2 = serial.Serial("COM2",9600)
        self.not_used2 = self.ser2.readline()
        """

    def StartReceiving(self, fromUdp: bool = False):
        """
        Receiving data from bending sensor and update self.bendingValue
        """

        # if fromUdp:
        #     sock = self.udpManager.sock

        #     try:
        #         while True:
        #             data, addr = self.udpManager.ReceiveData()
        #             self.bendingValue = float(data[0])

        #             # ----- (TEST) For Unity -----
        #             # triggerValue = float(data[data.index('trigger')+1])
        #             # self.bendingValue = (triggerValue - 0) / (1 - 0) * (800 - 0) + 0
        #             pass

        #     except OSError:
        #         print(
        #             "[OSError] UDPManager >> I/O related errors. Please check the UDP socket."
        #         )

        #     except KeyboardInterrupt:
        #         print("KeyboardInterrupt >> Stop: BendingSensorManager.py")

        # else:
        try:
            while True:
                # code3//ESP32からencoder受信(loadcell受信)
                line = self.ser.readline().decode("utf-8").rstrip()
                # データの抽出と変数への代入
                data_parts = line.split(",")
                self.bendingValue_int = int(
                    850 - int(data_parts[0]) / 1800 * 850
                )  # -425-0
                if self.bendingValue_int > 850:
                    self.bendingValue_int = 850
                elif self.bendingValue_int < 0:
                    self.bendingValue_int = 0
                self.bendingValue = self.bendingValue_int
                # print(bendingValue)
                # time.sleep(0.0001)
        except KeyboardInterrupt:
            print("KeyboardInterrupt >> Stop: BendingSensorManager.py")

    def EndReceiving(self):
        self.udpManager.CloseSocket()


# helloworld
