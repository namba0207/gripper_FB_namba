# loadcell読み取り
import threading
import time

from xarm.wrapper import XArmAPI


class ArmWrapper:
    def __init__(self):
            self.armIP = "192.168.1.242"
            self.arm = XArmAPI(self.armIP)
            self.loadcell_setup()
            self.loadcell_int = 0

    def loadcell_setup(self):
        self.arm.set_tgpio_modbus_baudrate(2000000)
        self.init_loadcell_val = self.arm.get_cgpio_analog(1)[1]  # 初期値ofssetと同じ//cはコントロールボックスのc (0)と(1)はピンの違い#get_cgpio_analogが読む関数coreは成功してるか
        self.loadcell_thr = threading.Thread(target=self.get_loadcell_val, daemon=True)
        self.loadcell_thr.start()

    def get_loadcell_val(self):
  
        while True:
            self.loadcell = (
                float(self.arm.get_cgpio_analog(1)[1]) - float(self.init_loadcell_val)
            ) * 1000

            print(self.loadcell)
            time.sleep(0.01)

if __name__ == "__main__":
    test = ArmWrapper()
    try:
        while True:
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("finish loop")