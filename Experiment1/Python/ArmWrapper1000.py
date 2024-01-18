# 1027,28オアシス用
import threading
import time

import numpy as np

# from sharedavatar import RobotConfig as RC
# from xarm import XArmAPI
from xarm.wrapper import XArmAPI


class ArmWrapper:
    def __init__(self, enable, armIP=None):
        if enable:
            self.arm = XArmAPI(armIP)
            self.loadcell_setup()
            # self.gripper_setup()
            self.loadcell_int = 0

    def loadcell_setup(self):
        self.arm.set_tgpio_modbus_baudrate(2000000)
        self.init_loadcell_val = self.arm.get_cgpio_analog(1)[
            1
        ]  # 初期値ofssetと同じ//cはコントロールボックスのc
        self.loadcell_thr = threading.Thread(target=self.get_loadcell_val, daemon=True)
        self.loadcell_thr.start()

    def get_loadcell_val(self):
        #         self.loadcell_val = (
        #             self.arm.get_cgpio_analog(1)[1] - self.init_loadcell_val
        #         )  # (0)と(1)はピンの違い#get_cgpio_analogが読む関数coreは成功してるか
        while True:
            self.loadcell = (
                float(self.arm.get_cgpio_analog(1)[1]) - float(self.init_loadcell_val)
            ) * 1000
            if self.loadcell > 200:
                self.loadcell = 200
            elif self.loadcell < 0:
                self.loadcell = 0
            self.loadcell_int = int(self.loadcell / (200 - 0) * (255 - 127) + 127)
            time.sleep(0.001)

    # def gripper_setup(self):
    #     code = self.arm.set_gripper_mode(0)
    #     print("set gripper mode: location mode, code={}".format(code))

    #     code = self.arm.set_gripper_enable(True)
    #     print("set gripper enable, code={}".format(code))

    #     code = self.arm.set_gripper_speed(5000)
    #     print("set gripper speed, code={}".format(code))

    # self.t = time.perf_counter()

    # self.gripper_thr = threading.Thread(target=self.set_gripper_val, daemon=True)
    # self.gripper_thr.start()

    # def set_gripper_val(self):
    def ConvertToModbusData(self, value: int):
        if int(value) <= 255 and int(value) >= 0:
            dataHexThirdOrder = 0x00
            dataHexAdjustedValue = int(value)

        elif int(value) > 255 and int(value) <= 511:
            dataHexThirdOrder = 0x01
            dataHexAdjustedValue = int(value) - 256

        elif int(value) > 511 and int(value) <= 767:
            dataHexThirdOrder = 0x02
            dataHexAdjustedValue = int(value) - 512

        elif int(value) > 767 and int(value) <= 1123:
            dataHexThirdOrder = 0x03
            dataHexAdjustedValue = int(value) - 768

        modbus_data = [0x08, 0x10, 0x07, 0x00, 0x00, 0x02, 0x04, 0x00, 0x00]
        modbus_data.append(dataHexThirdOrder)
        modbus_data.append(dataHexAdjustedValue)

        return modbus_data

        # while True:
        #     gripper_val = 200 * (np.sin(2 * np.pi * 0.5 * (time.perf_counter() - self.t)) + 2)
        #     self.arm.getset_tgpio_modbus_data(ConvertToModbusData(gripper_val))
        #     time.sleep(0.01)
