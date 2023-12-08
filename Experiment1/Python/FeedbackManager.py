import threading
import time

import numpy as np
import pyaudio
import serial

# from BendingSensor.test import Test


class Vibrotactile:
    def __init__(self) -> None:
        self.rate = 48000
        self.freq = 200
        self.chunk = int(self.rate / self.freq)
        self.sin = np.sin(2.0 * np.pi * np.arange(self.chunk) * self.freq / self.rate)
        self.ampL = 11000
        self.ampR = 11000
        self.data_outL = 1
        self.data_outR = 1
        self.p = pyaudio.PyAudio()
        self.bendingValue = 850
        self.pretime = 0
        self.bendingVelocity = 0
        self.flag = 0
        # self.test = Test()
        # self.test_start = self.test.start()

        self.thr = threading.Thread(target=self.thread)
        self.thr.setDaemon(True)
        self.thr.start()

        self.streamL = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk,
            output_device_index=37,  # ファイルで探すやつ
            stream_callback=self.callback1,
        )
        self.streamL.start_stream()

        self.streamR = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk,
            output_device_index=39,  # ファイルで探すやつ
            stream_callback=self.callback2,
        )
        self.streamR.start_stream()

    def callback1(self, in_data, frame_count, time_info, status):
        if self.bendingVelocity > 2000:
            self.data_outL = 1
            self.flag = 1
            print("index")
        else:
            self.data_outL = 0
        out_data = (int(self.ampL * self.data_outL) * self.sin).astype(
            np.int16
        )  # 振幅をインスタンス変数で速度にしたり
        # print(int(self.amp * self.data_out))
        # print(self.flag)
        return (out_data, pyaudio.paContinue)

    def callback2(self, in_data, frame_count, time_info, status):
        if self.bendingVelocity < -2000:
            self.data_outR = 1
            print("back")
        else:
            self.data_outR = 0
        out_data = (int(self.ampR * self.data_outR) * self.sin).astype(
            np.int16
        )  # 振幅をインスタンス変数で速度にしたり
        # print(int(self.amp2 * self.data_out))
        # print(self.bendingValue)
        return (out_data, pyaudio.paContinue)

    def thread(self):
        self.ser = serial.Serial("COM8", 115200)
        try:
            while True:
                # code3//ESP32からencoder受信(loadcell受信)
                self.line = self.ser.readline().decode("utf-8").rstrip()
                # データの抽出と変数への代入
                self.data_parts = self.line.split(",")
                self.bendingValue_sub = int(
                    850 - int(self.data_parts[1].rstrip()) / 2800 * 850
                )
                if self.bendingValue_sub > 850:
                    self.bendingValue_sub = 850
                elif self.bendingValue_sub < 0:
                    self.bendingValue_sub = 0
                self.bendingVelocity = (self.bendingValue - self.bendingValue_sub) / (
                    time.perf_counter() - self.pretime
                )
                self.bendingValue = self.bendingValue_sub
                self.pretime = time.perf_counter()
                # print(self.bendingVelocity)
                # time.sleep(0.005)
        except KeyboardInterrupt:
            print("KeyboardInterrupt >> Stop: BendingSensorManager.py")

    def close(self):
        self.p.terminate()


if __name__ == "__main__":
    vibro = Vibrotactile()

    start_time = time.perf_counter()

    try:
        while True:
            print(time.perf_counter() - start_time)
            time.sleep(0.005)

    except KeyboardInterrupt:
        vibro.streamR.stop_stream()
        vibro.streamR.close()
        vibro.streamL.stop_stream()
        vibro.streamL.close()
        vibro.close()
        print("finish loop")
# source env/bin/activate
