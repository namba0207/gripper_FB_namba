import csv
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
        # self.finish_time = 0
        self.flag = 0
        self.flag_start = 0
        self.flag_display = 0
        self.next_time = 0
        self.count = 1

    def press(self, key):
        try:
            if format(key.char) == "s" and self.flag_start == 0:
                print("start")
                self.flag_start = 1
        except AttributeError:
            pass

    def process_udp_datagrams(self):

            while self.udp_socket.hasPendingDatagrams():
                datagram, host, port = self.udp_socket.readDatagram(
                    self.udp_socket.pendingDatagramSize()
                )
                data_list = datagram.data().decode().split(",")
                received_number = int(data_list[1])
                print_str = str(received_number)+ " 0"

                if self.flag_start == 1:
                    self.finish_time = time.perf_counter()
                    self.flag_start = 2
                elif self.flag_start == 2:

                    # display用のプログラム
                    if self.flag_display == 0:
                        self.flag_display = 1
                        self.start_time = time.perf_counter()
                    elif (time.perf_counter() - self.start_time < 1 and self.flag_display == 1):
                        print_str = "START"
                    else:

                        # クリアしていない場合
                        if (self.sum_time < 3 and self.flag !=3):
                            # flag = 1 から flag = 0のとき変換
                            if (received_number < 2000 and self.flag == 1):
                                self.flag = 0
                                print_str = str(received_number)+ " "+ str(int(self.sum_time))
                                self.sum_time_recode = self.sum_time
                            # flag = 2 から flag = 0のときセンサ0のときflag = 0
                            elif received_number == 0:
                                self.flag = 0
                                print_str = str(received_number)+ " " + str(int(self.sum_time))
                            # flag = 0 から flag = 1のとき変換、タイマースタート
                            if (received_number >= 2000 and self.flag == 0):
                                self.flag = 1
                                self.start_time_float = time.perf_counter()
                            # flag = 1 から flag = 2のとき変換、やり直し出力、カウントリセット
                            if (received_number >= 3500 or self.flag == 2):
                                self.flag = 2
                                print_str = "OUT"
                                # self.sum_time = 0
                                print("OUT")
                                sys.exit(app.exec_())

                            # メインの処理
                            if self.flag == 1:
                                self.sum_time = self.sum_time_recode + time.perf_counter() - self.start_time_float
                                print_str = str(received_number) + " "  + str(int(self.sum_time))

                        # 3秒以上キープした場合
                        elif self.flag == 1:
                            self.sum_time = 0
                            self.sum_time_recode = 0
                            self.flag = 3
                            self.next_time = time.perf_counter()

                        elif self.flag == 3:
                            print_str = "CLEAR" #+ str(self.count)

                        if time.perf_counter() - self.next_time > 1 and self.flag == 3:
                            print("CLEAR")
                            sys.exit(app.exec_())

                    if  time.perf_counter() - self.finish_time > 20:
                        print("timeover")
                        sys.exit(app.exec_())

                    with open("pressuredata0209taisukekakeya13.csv", "a", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow([time.perf_counter()-self.start_time,received_number])
                else:
                    pass
                # if (time.perf_counter() - self.next_time > 2 and self.count < 3 and self.flag == 3):
                #     self.flag = 0
                #     self.count += 1
                # elif (time.perf_counter() - self.next_time > 2 and self.count == 3 and self.flag == 3):
                #     sys.exit(app.exec_())
                # elif ( self.count == 3 and self.flag == 3):
                #     print_str = "FINISH"

                print(self.flag,self.next_time)
                self.center_label.setText(print_str)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CenterDisplayApp()
    listener = keyboard.Listener(on_press=window.press)
    listener.start()
    window.show()
    sys.exit(app.exec_())
