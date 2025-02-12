# Adioで小型6軸センサの値をUDP（pickle）で出力するプログラム！

import os
import pickle
import socket
import numpy as np

from serial import Serial
from serial.tools.list_ports import comports
from concurrent.futures import ThreadPoolExecutor


def search_port():
    ports = comports()
    os_name = os.name

    for port in ports:
        if os_name == "posix":
            if "usbserial-FT" in port.device:
                return port.device


def convert_data(data, input_voltage):
    MAX_ADC_VALUE = 524288
    __convert_data = []
    for i in range(0, len(data), 5):
        __data = int(data[i : i + 5], 16)
        if __data >= MAX_ADC_VALUE:
            __data -= MAX_ADC_VALUE * 2
        __convert_data.append((__data / MAX_ADC_VALUE) * input_voltage)
    return __convert_data


def parse_data(data):
    line = data.decode().strip()
    if line.startswith("*40"):
        ch = int(line[3], 16)
        data = convert_data(line[4:-1], input_voltage=5.0)
        return ch, data


def main():
    plot_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    SOCK_ADDRESS = ("localhost", 4000)

    ADC_CHANNEL_NUM = 16

    CHUNK_SIZE = 5
    CHUNK_NUM = 100

    REQUEST_DATA_NUM = 6

    handle = Serial(port=search_port(), timeout=1)
    handle.reset_input_buffer()
    handle.reset_output_buffer()

    # Reset the device
    buffer_reset = False
    while not buffer_reset:
        print("...", end="", flush=True)
        response = handle.readline()
        if response == b"":
            buffer_reset = True

    # Set conversion speed
    command = "*00000000#"
    handle.write(command.encode())
    response = handle.readline().decode().strip()
    if response:
        print(f"Response: {response}")
    else:
        print(f"No response or timeout for command: {command}")

    # Set the number of data acquisitions
    for i in range(ADC_CHANNEL_NUM):
        command = f"*10{i:X}0{format(CHUNK_SIZE, '04X')}#"
        handle.write(command.encode())
        response = handle.readline().decode().strip()
        if response:
            print(f"Response: {response}")
        else:
            print(f"No response or timeout for command: {command}")

    # Start memory accumulation
    handle.write("*40020000#".encode())
    response = handle.readline().decode().strip()
    if response:
        print(f"Response: {response}")
    else:
        print(f"No response or timeout for command: {command}")

    # Set the input voltage range
    for i in range(ADC_CHANNEL_NUM):
        command = f"*50{i:X}00001#"
        handle.write(command.encode())
        response = handle.readline().decode().strip()
        if response:
            print(f"Response: {response}")
        else:
            print(f"No response or timeout for command: {command}")

    # Request data transmission
    def send_data_request():
        for i in range(REQUEST_DATA_NUM):
            handle.write(f"*40{i:X}1{format(CHUNK_NUM-1, '04X')}#".encode())

    executor = ThreadPoolExecutor(max_workers=2)
    executor.submit(send_data_request)

    x = 0
    recv_chunk_count = 0
    # 右：SL241204
    transformation_matrix = np.array(
                [
                    [
                        0.82075,
                        -0.01557,
                        0.01833,
                        -0.00573,
                        0.13980,
                        -0.03723,
                    ],
                    [
                        0.01000,
                        0.85419,
                        0.02723,
                        -0.07019,
                        0.00863,
                        -0.04327,
                    ],
                    [
                        -0.00113,
                        0.00209,
                        1.00162,
                        0.00393,
                        0.00109,
                        -0.00561,
                    ],
                    [
                        0.00001,
                        0.00241,
                        0.00029,
                        0.00537,
                        -0.00001,
                        0.00005,
                    ],
                    [
                        -0.00227,
                        -0.00009,
                        -0.00009,
                        0.00006,
                        0.00503,
                        0.00004,
                    ],
                    [
                        -0.00001,
                        0.00003,
                        0.00005,
                        -0.00004,
                        -0.00003,
                        0.00186,
                    ],
                ]
            )
    # 左：SL241001
    # transformation_matrix = np.array(
    #             [
    #                 [
    #                     0.81444,
    #                     -0.03822,
    #                     0.00065,
    #                     -0.00110,
    #                     0.07771,
    #                     0.07022,
    #                 ],
    #                 [
    #                     0.01149,
    #                     0.83642,
    #                     -0.02069,
    #                     -0.05656,
    #                     0.00842,
    #                     -0.05572,
    #                 ],
    #                 [
    #                     0.00632,
    #                     -0.00594,
    #                     0.96449,
    #                     0.00358,
    #                     0.00042,
    #                     0.02417,
    #                 ],
    #                 [
    #                     0.00001,
    #                     0.00229,
    #                     -0.00008,
    #                     0.00508,
    #                     0.00001,
    #                     0.00019,
    #                 ],
    #                 [
    #                     -0.00221,
    #                     -0.00001,
    #                     -0.00004,
    #                     0.00003,
    #                     0.00495,
    #                     0.00011,
    #                 ],
    #                 [
    #                     0.00001,
    #                     0.00004,
    #                     0.00000,
    #                     0.00002,
    #                     -0.00002,
    #                     0.00171,
    #                 ],
    #             ]
    #         )
    while True:
        try:
            data_dict = {}

            for _ in range(REQUEST_DATA_NUM):
                response = handle.readline()
                parsed = parse_data(response)
                if parsed is not None:
                    ch, data = parsed
                    data_dict[ch] = data

            recv_chunk_count += 1
            if recv_chunk_count >= CHUNK_NUM * 0.8:
                recv_chunk_count = 0
                executor.submit(send_data_request)
                
            force_value = np.dot(
                transformation_matrix,
                np.array([d for d in data_dict.values()]),
                )*1000
            # force_value = np.array([d for d in data_dict.values()])

            x += 1
            plot_socket.sendto(
                pickle.dumps(
                    {
                        "x": x,
                        "y1": force_value[0].tolist(),
                        "y2": force_value[1].tolist(),
                        "y3": force_value[2].tolist(),
                        "y4": force_value[3].tolist(),
                        "y5": force_value[4].tolist(),
                        "y6": force_value[5].tolist(),
                    }
                ),
                SOCK_ADDRESS,
            )
            print(float(force_value[4][0])*100)


        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            break


if __name__ == "__main__":
    main()