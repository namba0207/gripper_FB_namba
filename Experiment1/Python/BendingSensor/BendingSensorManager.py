# -----------------------------------------------------------------------
# Author:   Takumi Katagiri (Nagoya Institute of Technology), Takayoshi Hagiwara (KMD)
# Created:  2021
# Summary:  曲げセンサからのデータ取得用マネージャー
# -----------------------------------------------------------------------

import serial

from UDP.UDPManager import UDPManager


class BendingSensorManager:

    bendingValue = 0

    def __init__(self, BendingSensor_connectionmethod, ip, port) -> None:
        self.ip             = ip
        self.port           = port
        self.bufsize        = 4096
        self.bendingValue   = 425

        if BendingSensor_connectionmethod == 'wireless':
            try:
                self.udpManager = UDPManager(port=self.port, localAddr=self.ip)
            except:
                print("could not open port: %s"%port)

        elif BendingSensor_connectionmethod == 'wired':
            try:
                self.serialObject = serial.Serial(ip, port, timeout=0.01)
                # not_used = self.serialObject.readline()
            except:
                print("could not open port: %s"%port)



    def StartReceiving(self, fromUdp: bool = False):
        """
        Receiving data from bending sensor and update self.bendingValue
        """
        if fromUdp:
            sock = self.udpManager.sock

            try:
                while True:
                    data, addr = self.udpManager.ReceiveData()
                    self.bendingValue = float(data[0])

            except OSError:
                print('[OSError] UDPManager >> I/O related errors. Please check the UDP socket.')

            except KeyboardInterrupt:
                print('KeyboardInterrupt >> Stop: BendingSensorManager.py')

        else:
            while True:
                try:
                    data = self.serialObject.readline()
                    self.bendingValue = float(data.strip().decode('utf-8'))
                    if self.bendingValue > 0.6:
                        self.bendingValue = 1.0

                except KeyboardInterrupt:
                    print('KeyboardInterrupt >> Stop: BendingSensorManager.py')

                except:
                    pass

    def EndReceiving(self):
        self.udpManager.CloseSocket()
