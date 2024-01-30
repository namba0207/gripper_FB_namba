# -*- coding: utf-8 -*-
from __future__ import print_function

import socket
import time
from contextlib import closing

# 送り先のIPアドレスとポート番号
host = "127.0.0.1"
port = 8888

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    while True:
        # 送る数値を一種類にする変数
        data_value = 100

        # 左右どちらかを選択して送信
        data = f"right,{data_value}"  # または "left,{data_value}"
        message = data.encode("utf-8")
        print(message)
        sock.sendto(message, (host, port))

        time.sleep(1)

