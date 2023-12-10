import threading
import time

import numpy as np
import pyaudio
import serial


class Vibrotactile:
    def __init__(self) -> None:
        self.rate = 48000
        self.freq = 200
        self.chunk = int(self.rate / self.freq)
        self.sin = np.sin(2.0 * np.pi * np.arange(self.chunk) * self.freq / self.rate)
        self.ampL = 11000
        self.ampR = 11000
        self.data_outL = 0
        self.data_outR = 0
        self.p = pyaudio.PyAudio()
        self.bendingValue = 850
        self.pretime = 0
        self.bendingVelocity = 0
        self.closetime = 0
        self.opentime = 0
        self.flag = 0
        self.thr_bend = threading.Thread(target=self.thread_bend)
        self.thr_bend.setDaemon(True)
        self.thr_bend.start()
        self.thr_flag = threading.Thread(target=self.thread_flag)
        self.thr_flag.setDaemon(True)
        self.thr_flag.start()

        self.streamL = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk,
            output_device_index=39,  # ファイルで探すやつ
            stream_callback=self.callback1,
        )
        self.streamL.start_stream()

        self.streamR = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk,
            output_device_index=37,  # ファイルで探すやつ
            stream_callback=self.callback2,
        )
        self.streamR.start_stream()

    def thread_bend(self):
        self.ser = serial.Serial("COM8", 115200)
        try:
            while True:
                # code3//ESP32からencoder受信(loadcell受信)
                self.line = self.ser.readline().decode("utf-8").rstrip()
                self.data_parts = self.line.split(",")
                self.bendingValue_sub = int(self.data_parts[1].rstrip())
                self.bendingVelocity = (self.bendingValue - self.bendingValue_sub) / (
                    time.perf_counter() - self.pretime
                )
                self.bendingValue = self.bendingValue_sub
                self.pretime = time.perf_counter()
                # print(self.data_parts)
        except KeyboardInterrupt:
            print("KeyboardInterrupt >> Stop: BendingSensorManager.py")

    def thread_flag(self):
        try:
            while True:
                # 閉じるとフラグが1になる。今の時間計測
                if self.bendingVelocity > 5000 and self.flag == 0:
                    self.flag = 1
                    self.closetime = time.perf_counter()
                # 開くとフラグが2になる。
                if self.bendingVelocity < -5000 and self.flag == 0:
                    self.flag = 2
                    self.opentime = time.perf_counter()
                time.sleep(0.005)
        except KeyboardInterrupt:
            print("KeyboardInterrupt >> Stop: BendingSensorManager.py")

    def callback1(self, in_data, frame_count, time_info, status):
        # フラグが1のとき任意の時間振動する！
        if self.flag == 1 and time.perf_counter() - self.closetime < 0.05:
            self.data_outL = 1

        # フラグが2のとき任意の時間振動する！振動後フラグ、opentimeを0に戻す
        elif (
            self.flag == 2
            and time.perf_counter() - self.opentime > 0.2
            and time.perf_counter() - self.opentime < 0.25
        ):
            self.data_outL = 1
            # print(222)
        elif self.flag == 2 and time.perf_counter() - self.opentime > 0.25:
            self.flag = 0
            self.opentime = 0

        # その他は0
        else:
            self.data_outL = 0

        out_data = (int(self.ampL * self.data_outL) * self.sin).astype(np.int16)
        return (out_data, pyaudio.paContinue)

    def callback2(self, in_data, frame_count, time_info, status):
        # フラグが2のとき任意の時間振動する！
        if self.flag == 2 and time.perf_counter() - self.opentime < 0.05:
            self.data_outR = 1

        # フラグが1のとき任意の時間振動する！振動後フラグ、opentimeを0に戻す
        elif (
            self.flag == 1
            and time.perf_counter() - self.closetime > 0.2
            and time.perf_counter() - self.closetime < 0.25
        ):
            self.data_outR = 1
            # print(111)
        elif self.flag == 1 and time.perf_counter() - self.closetime > 0.25:
            self.flag = 0
            self.closetime = 0

        # その他は0
        else:
            self.data_outR = 0

        out_data = (int(self.ampR * self.data_outR) * self.sin).astype(np.int16)
        return (out_data, pyaudio.paContinue)

    def close(self):
        self.p.terminate()


if __name__ == "__main__":
    vibro = Vibrotactile()

    try:
        while True:
            print(vibro.flag)
            time.sleep(0.005)

    except KeyboardInterrupt:
        vibro.streamR.stop_stream()
        vibro.streamR.close()
        vibro.streamL.stop_stream()
        vibro.streamL.close()
        vibro.close()
        print("finish loop")
# source env/bin/activate
