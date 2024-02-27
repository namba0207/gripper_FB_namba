# -----------------------------------------------------------------------
# Author:   Takayoshi Hagiwara (KMD)
# Created:  2021/8/25
# Summary:  Experiment manager
# -----------------------------------------------------------------------

# import threading
# import time
from ctypes import windll

import RobotArmController.Robotconfig_flag as RF

# from pynput import keyboard
from RobotArmController.RobotControlManager import RobotControlManager

# class Key_Class:
#     def __init__(self):
#         thr0 = threading.Thread(target=self.keyloop)
#         thr0.setDaemon(True)
#         thr0.start()
#         RF.pressure_flag = 0

#     def press(self, key):
#         try:
#             print(format(key))
#         except KeyboardInterrupt:
#             pass

#     def keyloop(self, key):
#         try:
#             while True:
#                 if format(key.char) == "s":
#                     RF.pressure_flag = 1
#         except KeyboardInterrupt:
#             pass
#             # time.sleep(0.005)


if __name__ == "__main__":
    # key_class = Key_Class()
    # listener = keyboard.Listener(on_press=key_class.press)
    # listener.start()
    robotControlManager = RobotControlManager()
    # ----- Debug mode ----- #
    robotControlManager.SendDataToRobot(
        participantNum=2,
        executionTime=9999,
        frameRate=150,
        isFixedFrameRate=False,
        isChangeOSTimer=False,
        isExportData=False,
        isEnablexArm=True,
    )

    print("\n----- End program: ExManager.py -----")
# AttributeError: module 'numpy' has no attribute 'quaternion'の場合、何も設定いじってなければ一度全部電源切って再起動する！2024/01/23
# numpyでモーキャプ取れてて、ロボ動かない、剛体のID番号が1、2になってない！！キャリブレーション後には１，２にしてやり直す。
# numpy quaetrnionのとき、基本的な剛体座標とれるか見た後に戻ってる。2024/01/31
