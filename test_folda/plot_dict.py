# dictのテキストをグラフに表示する

import matplotlib.pyplot as plt
import ast
import numpy as np

def load_data(file_path):
    """
    テキストファイルからデータを読み込む関数。
    1行目をスキップし、各行が辞書形式のデータとして保存されていることを想定。
    """
    data = []
    with open(file_path, 'r') as file:
        for index, line in enumerate(file):
            if index == 0:  # 1行目をスキップ
                continue
            try:
                data.append(ast.literal_eval(line.strip()))
            except Exception as e:
                print(f"データの読み込み中にエラーが発生: {e}")
    return data

def plot_data(data):
    y_values = {f'y{i}': [] for i in range(1, 7)}  # y1 ～ y6 の辞書

    # データの格納
    for entry in data:
        for i in range(1, 7):
            key = f'y{i}'
            if key in entry and isinstance(entry[key], list):
                y_values[key].extend(entry[key])  # **全ての値を追加**

    # **時間軸の作成**（1/10000 秒間隔でプロット）
    total_points = len(next(iter(y_values.values())))  # 最初のリストの長さ
    time = np.arange(0, total_points) / 10000  # **1/10000 秒刻みの時間軸**

    # 3行2列のサブプロットを作成
    fig, axes = plt.subplots(3, 2, figsize=(12, 8))
    fig.suptitle("Sensor Data Plots", fontsize=14)

    for i, (key, values) in enumerate(y_values.items()):
        row, col = divmod(i, 2)  # 3行2列の配置を計算
        axes[row, col].plot(time[:len(values)], values, label=key)  # **時間軸とデータの長さを調整**
        axes[row, col].legend()
        axes[row, col].grid(True)
        axes[row, col].set_xlabel("Time (s)")
        axes[row, col].set_ylabel(key)
        axes[row, col].set_ylim(-5, 5)

    plt.tight_layout(rect=[0, 0, 1, 0.96])  # タイトルとサブプロットのレイアウト調整
    plt.show()

# メイン処理
if __name__ == "__main__":
    file_path = "/Users/sanolab/Documents/GitHub/gripper_FB_namba/data0211satoru/main_data/data0211_2Hz.txt"

    data = load_data(file_path)
    plot_data(data)
