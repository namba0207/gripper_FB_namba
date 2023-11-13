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
    bendingValue = 0

    def __init__(self, port) -> None:
        # self.ip = ip
        # self.port = port
        # self.bufsize = 4096
        # self.bendingValue = 425
        self.bendingValue = 1

        # wireless
        # self.udpManager = UDPManager(port=self.port, localAddr=self.ip)

        # serial
        # self.serialObject = serial.Serial(ip, port)
        # nonUsed = self.serialObject.readline()
        self.arduino_port = 'COM3'
        self.baud_rate = 115200
        self.ser = serial.Serial(self.arduino_port, self.baud_rate)
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

        # else:いえい
        try:
            while True:
                # data = self.serialObject.readline()
                # self.bendingValue = float(data.strip().decode('utf-8'))
                #code3//ESP32からencoder受信(loadcell受信)
                line = self.ser.readline().decode('utf-8').rstrip()
                # データの抽出と変数への代入
                data_parts = line.split(',')
                pos1 = int(850+float(data_parts[0])/1600*850)#-425-0
                
                self.bendingValue = 1
                print(11111)
                time.sleep(0.05)

        except KeyboardInterrupt:
            print("KeyboardInterrupt >> Stop: BendingSensorManager.py")

    def EndReceiving(self):
        self.udpManager.CloseSocket()
