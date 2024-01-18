import time
import math
start_time = time.perf_counter()
e = math.e
number = 10
oshikomi = 200  #oshikomiまで移動する
while True:
    try:
        data1 = time.perf_counter() - start_time
        if data1 < 1:
            data2 = 400
        elif data1 < 20/number + 1:
            data2 = 400 - (400 - oshikomi) / (1 + e**-((data1-1)*number-10))
        elif data1 < 20/number + 2:
            data2 = oshikomi
        elif data1 < 20/number*2 + 2:
            data2 = 400 - (400 - oshikomi) / (1 + e**(((data1-1)*number-31-number)))
        else:
            data2 = 400
    except KeyboardInterrupt:
            print("KeyboardInterrupt Stop:program")
            break