#loadcellの値を表示するだけ
import threading
import time

from xarm import XArmAPI


class ArmWrapper:
    def __init__(self, enable, armIP=None):
        if enable:
            self.arm = XArmAPI(armIP)
            self.loadcell_val0 = 0
            self.loadcell_val1 = 0
            self.loadcell_setup()

    def loadcell_setup(self):
        # self.arm.set_tgpio_modbus_baudrate(2000000)
        self.init_loadcell_val0 = self.arm.get_cgpio_analog(0)[1]#初期値ofssetと同じ//cはコントロールボックスのc
        self.init_loadcell_val1 = self.arm.get_cgpio_analog(1)[1]
        self.loadcell_thr = threading.Thread(target=self.get_loadcell_val, daemon=True)
        self.loadcell_thr.start()

    def get_loadcell_val(self):
        while True:
            self.loadcell_val0 = abs(self.arm.get_cgpio_analog(0)[1] - self.init_loadcell_val0)#(0)と(1)はピンの違い#get_cgpio_analogが読む関数//coreは成功してるかどうか//
            self.loadcell_val1 = abs(self.arm.get_cgpio_analog(1)[1] - self.init_loadcell_val1)
            time.sleep(0.01)

if __name__ == "__main__":
    ip = '192.168.1.242'
    armwapper = ArmWrapper(True,ip)

    while True:
        feedback_data = "{:.3f}".format(armwapper.loadcell_val0),"{:.3f}".format(armwapper.loadcell_val1)
        print(feedback_data)
        time.sleep(0.01)
