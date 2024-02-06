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
flag = 0
sum_time = 0
count = 1

# data_parts = line.split(",")
# bendingValue_int = int(data_parts[0].rstrip())

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    while True:
        # 送る数値を一種類にする変数
        data_value = ser.readline().decode("utf-8").rstrip()
        if sum_time < 300:
            if int(data_value) >= 3000 and flag == 0:
                flag = 1
                start_time = time.perf_counter()*100
            if int(data_value) >= 3000 and int(data_value) < 3500 and flag == 1:
                sum_time = sum_time + time.perf_counter()*100 - start_time
                data_value = data_value + str(int(sum_time))
            if int(data_value) >= 3500 and flag == 1:
                flag = 2
                sum_time = 0
                data_value = 'RETRY'
            if int(data_value) < 3000 and flag == 1:
                data_value = 'CONTINUE'
            if int(data_value)  == 0:
                flag = 0
        else:
            next_time = time.perf_counter()
            flag = 3
        if time.perf_counter() - next_time < 3 and flag == 3:
            data_value = 'CLEAR' + str(count)
        elif flag == 3:
            sum_time = 0
            flag = 0
            count += 1
        # print(data_value)
        # 左右どちらかを選択して送信
        data = f"right,{data_value}"  # または "left,{data_value}"
        message = data.encode("utf-8")
        print(message)
        sock.sendto(message, (host, port))
        # time.sleep(0.01)
