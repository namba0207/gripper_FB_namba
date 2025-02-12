# グラフにプロットする

import time
import matplotlib.pyplot as plt
from UDP_server_pickle import UDP_Server_Pickle

def main():
    # サーバーの初期化
    udp_server = UDP_Server_Pickle("localhost", 4000)  # IP とポート番号を指定
    udp_server.receive_start()  # データ受信を開始

    # グラフの初期設定
    plt.ion()  # インタラクティブモードを有効化
    fig, ax = plt.subplots()
    x_data = []  # 時間軸データ
    y_data_list = [[] for _ in range(6)]  # 6つのUDP受信データを格納

    # 6本の線を準備
    lines = [ax.plot([], [], lw=2, label=f"Line {i+1}")[0] for i in range(6)]

    # グラフの余白設定
    ax.set_xlim(-1.3, 0.3)  # x軸の初期範囲
    ax.set_ylim(-10, 10)  # y軸の初期範囲（適宜変更）
    ax.legend(loc="upper right")  # 凡例を追加

    start_time = time.time()

    while True:
        try:
            # データ取得
            current_time = time.time() - start_time
            if udp_server.force_values:
                # 各force_valuesからデータを取得
                for i in range(6):
                    received_value = udp_server.force_values[i][0]  # 受信データの1つ目を使用
                    if i == 3:
                        received_value = received_value*10
                    if i == 4:
                        received_value = received_value*10

                    y_data_list[i].append(received_value)

                    # データ数を100点に制限
                    if len(y_data_list[i]) > 100:
                        y_data_list[i].pop(0)

                # 時間軸データを更新
                x_data.append(current_time)
                if len(x_data) > 100:
                    x_data.pop(0)

                # 各線を更新
                for i in range(6):
                    lines[i].set_data(x_data, y_data_list[i])

                # 動的に軸範囲を調整
                ax.set_xlim(max(0, current_time - 1.3), current_time + 0.3)
                # ax.set_ylim(min(min(y) for y in y_data_list if y) - 0.1, 
                #             max(max(y) for y in y_data_list if y) + 0.1)

                # グラフを更新
                plt.pause(0.001)

        except KeyboardInterrupt:
            print("グラフ描画を終了します")
            break

if __name__ == "__main__":
    main()
