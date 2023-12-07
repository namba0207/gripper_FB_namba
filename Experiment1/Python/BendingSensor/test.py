import time

import serial


class Test:
    def __init__(self) -> None:
        self.ser = serial.Serial("COM8", 115200)

    def start(self):
        try:
            while True:
                # code3//ESP32からencoder受信(loadcell受信)
                self.line = self.ser.readline().decode("utf-8").rstrip()
                # データの抽出と変数への代入
                self.data_parts = self.line.split(",")
                self.bendingValue_sub = int(
                    850 - int(self.data_parts[0].rstrip()) / 2700 * 850
                )
                if self.bendingValue_sub > 850:
                    self.bendingValue_sub = 850
                elif self.bendingValue_sub < 0:
                    self.bendingValue_sub = 0
                self.bendingValue = self.bendingValue_sub
                print(self.bendingValue_sub)
        except KeyboardInterrupt:
            print("KeyboardInterrupt >> Stop: BendingSensorManager.py")


# ser = serial.Serial("COM8", 115200)

# try:
#     while True:
#         # code3//ESP32からencoder受信(loadcell受信)
#         line = ser.readline().decode("utf-8").rstrip()
#         # データの抽出と変数への代入
#         data_parts = line.split(",")
#         bendingValue_sub = int(850 - int(data_parts[0].rstrip()) / 2700 * 850)
#         if bendingValue_sub > 850:
#             bendingValue_sub = 850
#         elif bendingValue_sub < 0:
#             bendingValue_sub = 0
#         bendingValue = bendingValue_sub
#         print(data_parts)
# except KeyboardInterrupt:
#     print("KeyboardInterrupt >> Stop: BendingSensorManager.py")
