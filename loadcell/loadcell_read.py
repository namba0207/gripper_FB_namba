# センサ（loadcell）の値を表示するプログラム
# xarmのAPIを使用、__version__ = "1.13.19"
import threading
import time

from xarm import XArmAPI

class ArmWrapper:
    def __init__(self, enable, armIP=None):
        if enable:
            self.arm = XArmAPI(armIP)
            self.loadcell_val = 0
            self.loadcell_setup()

    def loadcell_setup(self):
        self.arm.set_tgpio_modbus_baudrate(2000000)
        self.init_loadcell_val = self.arm.get_cgpio_analog(0)[1]
        self.loadcell_thr = threading.Thread(target=self.get_loadcell_val, daemon=True)
        self.loadcell_thr.start()

    def get_loadcell_val(self):
        while True:
            self.loadcell_val0 = abs(self.arm.get_cgpio_analog(0)[1] - self.init_loadcell_val)
            time.sleep(0.01)

if __name__ == "__main__":
    ip = '192.168.1.242'
    armwapper = ArmWrapper(True,ip)

    while True:
        feedback_data = "{:.3f}".format(armwapper.loadcell_val0),"{:.3f}".format(armwapper.loadcell_val)
        print(feedback_data)
        time.sleep(0.01)