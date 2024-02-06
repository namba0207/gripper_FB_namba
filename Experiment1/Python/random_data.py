import csv
import random
from random import randint

# 人肌ゲル順番
sample_list = [1, 2, 4]
i = 0
while i < 9:
    num1 = randint(1, 2)
    num2 = randint(1, 2)
    num3 = randint(1, 2)
    num = random.sample(sample_list, 3)
    print(num1,num2,num3,num)

    with open("data0206.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                num1,
                num2,
                num3,
                num
            ]
        )
    i += 1
