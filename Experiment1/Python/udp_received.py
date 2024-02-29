import csv
import math
import sys
import time

from pynput import keyboard, mouse
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtNetwork import QUdpSocket
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class CenterDisplayApp(QWidget):
    def __init__(self):
        super().__init__()

        # ウィンドウの初期設定
        self.setWindowTitle("UDP Communication App")
        self.setGeometry(100, 100, 600, 400)

        # レイアウトの設定
        main_layout = QVBoxLayout(self)

        # 中央のウィジェット
        self.center_label = QLabel("-", alignment=Qt.AlignCenter)
        main_layout.addWidget(self.center_label)

        # UDP通信用の設定
        self.udp_socket = QUdpSocket(self)
        self.udp_socket.bind(8888)  # ポート番号を8888に変更

        # UDPデータ受信時の処理を設定
        self.udp_socket.readyRead.connect(self.process_udp_datagrams)

        # フォントサイズを大きくする
        font = QFont()
        font.setPointSize(400)  # フォントサイズを300に設定
        self.center_label.setFont(font)

        self.sum_time = 0
        self.sum_time_recode = 0
        self.start_time = 0
        self.start_time_float = 0
        self.flag = 0
        self.flag_start = 0
        self.flag_display = 0
        self.flag_2000 = 0
        self.next_time = 0
        self.count = 1
        self.p_count = 0

    def press(self, key):
        try:
            if format(key) == "Key.enter":
                print("enter")
                self.p_count += 1
        except AttributeError:
            pass

    def process_udp_datagrams(self):
        e = math.e
        while self.udp_socket.hasPendingDatagrams():
            datagram, host, port = self.udp_socket.readDatagram(
                self.udp_socket.pendingDatagramSize()
            )
            data_list = datagram.data().decode().split(",")
            received_number = int(
                (0.343 * e ** (int(data_list[1]) / 500) + 152) * 9.8 / 1000
            )
            print_str = str(received_number)

            if self.p_count > 1 and self.flag_start == 0:
                print("start")
                self.flag_start = 1
            if self.flag_start == 1:
                print("pass")
                # self.finish_time = time.perf_counter()
                self.flag_start = 2
            elif self.flag_start == 2:

                # display用のプログラム
                if self.flag_display == 0:
                    self.flag_display = 1
                    self.start_time = time.perf_counter()
                elif (
                    time.perf_counter() - self.start_time < 1 and self.flag_display == 1
                ):
                    print_str = "START"
                else:
                    if self.sum_time < 1:
                        if (
                            received_number == 0
                            and self.flag_2000 == 1
                            or self.flag == 3
                        ) and self.flag != 2:
                            self.flag = 3
                            print_str = "RETRY"
                            print("RETRY")
                        elif received_number < 10 and self.flag == 2:
                            self.flag = 1
                            self.start_time_float = time.perf_counter()
                            self.sum_time = 0
                        elif received_number >= 10 or self.flag == 2:
                            self.flag = 2
                            print_str = str(received_number) + " " + "NG"
                            self.sum_time = 0
                            print("OVER")

                        if received_number < 6 and self.flag != 2 and self.flag != 3:
                            self.flag = 0
                            print_str = str(received_number) + " " + "NG"
                            self.sum_time = 0
                        # メインの処理
                        if received_number >= 6 and self.flag == 0:
                            self.flag = 1
                            self.flag_2000 = 1
                            self.start_time_float = time.perf_counter()
                        if self.flag == 1:
                            self.sum_time = time.perf_counter() - self.start_time_float
                            print_str = str(received_number) + " " + "OK"
                    else:
                        print("CLEAR")
                        if self.flag_display == 1:
                            self.flag_display = 2
                            self.clear_time = time.perf_counter()
                        elif (
                            time.perf_counter() - self.clear_time < 1
                            and self.flag_display == 2
                        ):
                            print_str = "CLEAR"
                        else:
                            sys.exit(app.exec_())

                with open("p0229.txt", "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        [
                            time.perf_counter() - self.start_time,
                            received_number,
                            self.sum_time,
                        ]
                    )
            else:
                pass

            print(self.flag, self.next_time)
            self.center_label.setText(print_str)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CenterDisplayApp()
    listener = keyboard.Listener(on_press=window.press)
    listener.start()
    window.show()
    sys.exit(app.exec_())
