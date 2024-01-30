import sys
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

    def process_udp_datagrams(self):
        while self.udp_socket.hasPendingDatagrams():
            datagram, host, port = self.udp_socket.readDatagram(
                self.udp_socket.pendingDatagramSize()
            )
            data_list = datagram.data().decode().split(",")
            received_number = int(data_list[1])
            self.center_label.setText(str(received_number))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CenterDisplayApp()
    window.show()
    sys.exit(app.exec_())
