# -*- coding: utf-8 -*-
from __future__ import print_function

import socket
import time
from contextlib import closing

import serial

# 送り先のIPアドレスとポート番号
host = "127.0.0.1"
port = 8888

ser = serial.Serial("COM8", 115200)
not_used = ser.readline()

# data_parts = line.split(",")
# bendingValue_int = int(data_parts[0].rstrip())

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    while True:
        # 送る数値を一種類にする変数
        data_value = ser.readline().decode("utf-8").rstrip()
        # print(data_value)
        # 左右どちらかを選択して送信
        data = f"right,{data_value}"  # または "left,{data_value}"
        message = data.encode("utf-8")
        print(message)
        sock.sendto(message, (host, port))
        # time.sleep(0.01)
