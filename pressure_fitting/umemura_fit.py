# %%
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# テキストファイルをカンマ区切りで読み込む
data = np.genfromtxt("/Users/sanolab/Documents/GitHub/gripper_FB_namba/kousei_result_satoru0211/data_kouseiL1.txt")
print(data.shape)
# x, yデータを抽出
x_data = data[:, 0]  # 1列目がxデータ
y_data = data[:, 1]  # 2列目がyデータ

# 定数 Rm
Rm = 1000

# 近似曲線の関数定義
def model(x, a, b):
    return 5 * Rm / (Rm + a * x**b)

# 曲線フィッティング
params, covariance = curve_fit(model, x_data, y_data, p0=[1, 1])  # 初期値p0=[1, 1]を設定
a, b = params

# フィットした結果を表示
print(f"推定値: a = {a:.6f}, b = {b:.6f}")

# 元データとフィットした曲線をプロット
plt.figure(figsize=(8, 6))
plt.scatter(x_data, y_data, color="blue")
plt.plot(x_data, model(x_data, a, b), color="red")
plt.xlabel("x")
plt.ylabel("y")
# plt.legend()
# plt.title("データと近似曲線")
plt.show()
# %%
