import time

import numpy as np
import pyaudio


class Vibrotactile:
    def __init__(self) -> None:
        self.rate = 48000
        self.freq = 200
        self.chunk = int(self.rate / self.freq)
        self.sin = np.sin(2.0 * np.pi * np.arange(self.chunk) * self.freq / self.rate)
        self.ampL = 11000
        self.ampR = 1100
        self.data_out = 0
        self.p = pyaudio.PyAudio()

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
        # self.data_out = 0
        out_data = (int(self.ampL * self.data_out) * self.sin).astype(
            np.int16
        )  # 振幅をインスタンス変数で速度にしたり
        # print(int(self.amp * self.data_out))
        return (out_data, pyaudio.paContinue)

    def callback2(self, in_data, frame_count, time_info, status):
        # self.data_out = 0
        out_data = (int(self.ampR * self.data_out) * self.sin).astype(
            np.int16
        )  # 振幅をインスタンス変数で速度にしたり
        # print(int(self.amp2 * self.data_out))
        return (out_data, pyaudio.paContinue)

    def close(self):
        self.p.terminate()


if __name__ == "__main__":
    vibro = Vibrotactile()
    vibro.data_out = 1
    start_time = time.perf_counter()

    try:
        while True:
            print(time.perf_counter() - start_time)
            time.sleep(0.005)

    except KeyboardInterrupt:
        vibro.stream.stop_stream()
        vibro.stream.close()
        vibro.close()
        print("finish loop")
# source env/bin/activate
