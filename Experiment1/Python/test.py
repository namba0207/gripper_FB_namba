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
from scipy import stats as st
from xarm.wrapper import XArmAPI


class BendingSensorManager:
    def __init__(self) -> None:
        self.slope_h = 0
        self.pos2 = 0
        self.x_data = np.array([0])
        self.x_data = np.array([0])
        self.flag = 0
        self.bendingValue = 400
        self.bendingValue_sub = 0
        self.ser = serial.Serial("COM10", 115200)  # グリッパー操作
        self.ser2 = serial.Serial("COM7", 115200)  # 柔らかさFB
        self.not_used = self.ser.readline()
        self.not_used = self.ser2.readline()
        self.arm = XArmAPI("192.168.1.199")

    # def sendloop(self):
    #     while True:
    #         # self.num_str = str(RC.num_int) + "," + str(self.pos2) + "\n"
    #         self.num_str = str(RC.num_int) + "\n"
    #         self.ser.write(self.num_str.encode())
    #         time.sleep(0.005)

    def sendloop2(self):
        slope = 0
        while True:
            # 掴み始め・離し始め
            if (
                self.flag == 0
                and RC.num_int >= 128
                # and self.arm.get_gripper_position()[1] < 270
            ):
                self.grippos = self.arm.get_gripper_position()[1]
                self.flag = 1
            elif RC.num_int < 128 or self.arm.get_gripper_position()[1] > self.grippos:
                self.grippos = 0
                self.flag = 0

            if self.flag == 0:
                self.x_list = np.array([0])
                self.y_list = np.array([0])
                self.slope_h = 0
            else:
                self.x_list = np.append(
                    # self.x_list,
                    # [270 - self.arm.get_gripper_position()[1]],
                    self.x_list,
                    [self.grippos - self.arm.get_gripper_position()[1]],
                )
                self.y_list = np.append(self.y_list, [RC.num_int - 128])
                # データ数が10を超えたら古いデータを削除!!!最初の数字を(0,0)にしないと最小二乗法ですべての点が同じ時に傾きがぶれやすくなる！！
                if len(self.x_list) > 10:
                    self.x_list = self.x_list[2:]
                    self.y_list = self.y_list[2:]
                    self.x_list = np.insert(self.x_list, 0, 0)
                    self.y_list = np.insert(self.y_list, 0, 0)
                if len(self.x_list) >= 10:
                    self.x_data = np.array([self.x_list])
                    self.y_data = np.array([self.y_list])
                    if np.std(self.x_data) == 0:
                        pass
                    else:
                        slope, intercept, r_value, p_value, std_err = (
                            st.linregress(  # 最小二乗法
                                self.x_data[-1:-11:-1], self.y_data[-1:-11:-1]
                            )
                        )
                    if slope < 0.2 or slope > 3:
                        slope = 3
                    slope = 1 / slope
                    self.slope_h = int((slope - 1 / 3) * (255 - 0))
                    if self.slope_h > 200:
                        self.slope_h = 200
                    elif self.slope_h < 0:
                        self.slope_h = 0
            self.ser2.write(bytes([self.slope_h]))
            time.sleep(0.005)

    def StartReceiving(self):
        """
        Receiving data from bending sensor and update self.bendingValue
        """
        try:
            thr = threading.Thread(target=self.sendloop2)
            thr.setDaemon(True)
            thr.start()
            while True:
                self.line = self.ser.readline().decode("utf-8").rstrip()
                self.bendingValue_int = int(400 * float(self.line))
                if self.bendingValue_int > 400:
                    self.bendingValue_int = 400
                elif self.bendingValue_int < 200:
                    self.bendingValue_int = 200
                self.bendingValue = self.bendingValue_int
        except KeyboardInterrupt:
            print("KeyboardInterrupt >> Stop: BendingSensorManager.py")
