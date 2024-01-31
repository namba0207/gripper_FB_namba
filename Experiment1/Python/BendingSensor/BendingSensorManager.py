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
        self.x_data = np.array([])
        self.x_data = np.array([])
        self.flag = 0
        self.bendingValue = 400
        self.bendingValue_sub = 0
        self.ser = serial.Serial("COM8", 115200)
        self.ser2 = serial.Serial("COM7", 115200)
        self.not_used = self.ser.readline()
        self.not_used = self.ser2.readline()
        self.arm = XArmAPI("192.168.1.199")

    def sendloop(self):
        while True:
            # self.num_str = str(RC.num_int) + "," + str(self.pos2) + "\n"
            self.num_str = str(RC.num_int) + "\n"
            self.ser.write(self.num_str.encode())
            time.sleep(0.005)

    def sendloop2(self):
        while True:
            # 掴み始め・離し始め
            if self.flag == 0 and RC.num_int >= 129:
                self.grip = self.arm.get_gripper_position()[1]
                self.flag = 1
            elif RC.num_int < 129:
                self.grip = 0
                self.flag = 0
            if self.flag == 0:
                self.x_list = np.array([])
                self.y_list = np.array([])
                self.slope_h = 0
            else:
                self.pos2 = int(
                    (self.grip - self.arm.get_gripper_position()[1])
                    * (255 - 0)
                    / (self.grip - 200)  # 止まるところでグリッパー閉じ切る
                )
                self.x_list = np.append(
                    self.x_list, [self.grip - self.arm.get_gripper_position()[1]]
                )
                self.y_list = np.append(self.y_list, [RC.num_int - 129])
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
                        slope, intercept, r_value, p_value, std_err = st.linregress(
                            self.x_data[-1:-11:-1], self.y_data[-1:-11:-1]
                        )
                    # print("傾き:{0}".format(slope))
                    if slope < 0.1:
                        slope = 0.1
                    if slope > 3:
                        slope = 3
                    slope = 1 / slope
                    self.slope_h = int((slope - 0.3) * (255 - 0) / (10 - 0.3))
                    if self.slope_h > 100:
                        self.slope_h = 100
                    elif self.slope_h < 0:
                        self.slope_h = 0
            self.ser2.write(bytes([self.slope_h]))
            # print(self.slope_h)
            # self.ser.write(bytes([RC.num_int]))
            time.sleep(0.005)

    def StartReceiving(self):
        """
        Receiving data from bending sensor and update self.bendingValue
        """
        try:
            thr = threading.Thread(target=self.sendloop)
            thr.setDaemon(True)
            thr.start()
            thr = threading.Thread(target=self.sendloop2)
            thr.setDaemon(True)
            thr.start()
            while True:
                line = self.ser.readline().decode("utf-8").rstrip()
                # # line2 = self.ser2.readline().decode("utf-8").rstrip()
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
                # print(
                #     self.data_parts,
                #     # line2,
                #     RC.num_int,
                #     self.arm.get_gripper_position()[1],
                # )
                # time.sleep(0.005)
        except KeyboardInterrupt:
            print("KeyboardInterrupt >> Stop: BendingSensorManager.py")
