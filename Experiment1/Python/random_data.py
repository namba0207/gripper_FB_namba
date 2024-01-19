import random
from random import randint

# 条件順番
# l = ["A", "B", "C", "D", "E", "F"]
# random.shuffle(l)
# print(l)
data = []
# 人肌ゲル順番
sample_list = [1, 2, 4]
combined_list = []
i = 0
while i < 9:
    num1 = randint(1, 2)
    num2 = randint(1, 2)
    num3 = randint(1, 2)
    num = random.sample(sample_list, 3)
    combined_list_new = [[num1, num2, num3], num]
    combined_list = combined_list + combined_list_new
    print(combined_list_new)
    j = 0
    oshikomi = []
    speed = []
    while j < 3:
        if num[j] == 1:
            oshikomi += [random.choice((150, 230))]
        if num[j] == 2:
            oshikomi += [random.choice((170, 240))]
        if num[j] == 4:
            oshikomi += [random.choice((190, 250))]
        j += 1
    speed = [
        random.choice((10, 20, 40)),
        random.choice((10, 20, 40)),
        random.choice((10, 20, 40)),
    ]
    # print("[",num1,num2,num3,"]",num)
    k = 0
    while k < 3:
        print("self.oshikomi, self.number = ", oshikomi[k], ",", speed[k])
        k += 1
    print()
    i += 1
i = 0
while i < 18:
    print(combined_list[i], combined_list[i + 1])
    i += 2

# self.oshikomi, self.number = 170, 40
# self.oshikomi, self.number = 150, 40
# self.oshikomi, self.number = 190, 40

# self.oshikomi, self.number = 230, 40
# self.oshikomi, self.number = 250, 10
# self.oshikomi, self.number = 210, 10

# self.oshikomi, self.number = 230, 10
# self.oshikomi, self.number = 210, 10
# self.oshikomi, self.number = 250, 20

# self.oshikomi, self.number = 250, 20
# self.oshikomi, self.number = 210, 20
# self.oshikomi, self.number = 230, 10

# self.oshikomi, self.number = 250, 10
# self.oshikomi, self.number = 150, 40
# self.oshikomi, self.number = 230, 10

# self.oshikomi, self.number = 210, 20
# self.oshikomi, self.number = 170, 10
# self.oshikomi, self.number = 190, 10

# self.oshikomi, self.number = 210, 40
# self.oshikomi, self.number = 170, 10
# self.oshikomi, self.number = 190, 10

# self.oshikomi, self.number = 230, 40
# self.oshikomi, self.number = 250, 10
# self.oshikomi, self.number = 150, 10

# self.oshikomi, self.number = 250, 40
# self.oshikomi, self.number = 210, 20
# self.oshikomi, self.number = 230, 10

# [2, 2, 2] [2, 1, 4]
# [2, 1, 1] [2, 4, 1]
# [2, 2, 1] [2, 1, 4]
# [1, 1, 1] [4, 1, 2]
# [1, 2, 2] [4, 1, 2]
# [1, 2, 2] [1, 2, 4]
# [1, 1, 2] [1, 2, 4]
# [2, 1, 2] [2, 4, 1]
# [2, 2, 2] [4, 1, 2]
# 0119data
