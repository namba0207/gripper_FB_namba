import random
from random import randint

# 人肌ゲル順番
sample_list = [1, 2, 4]
sample_list_pra = [1, 5]
combined_list = []
combined_new = []
combined_pre = []
i = 0
while i < 3:
    num = random.sample(sample_list_pra, 2)
    print(num)
    j = 0
    oshikomi = []
    speed = []
    while j < 2:
        if num[j] == 1:
            oshikomi += [random.choice((160, 220))]
        if num[j] == 5:
            oshikomi += [random.choice((210, 250))]
        j += 1
    speed = [
        random.choice((0.5, 1, 2)),
        random.choice((0.5, 1, 2)),
        random.choice((0.5, 1, 2)),
    ]
    k = 0
    while k < 2:
        print("self.oshikomi, self.speed = ", oshikomi[k], ",", speed[k])
        k += 1
    i += 1

# i = 0
# while i < 9:
#     print(i + 1)
#     num1 = randint(1, 2)
#     num2 = randint(1, 2)
#     num3 = randint(1, 2)
#     num = random.sample(sample_list, 3)
#     combined_list_new = [[num1, num2, num3], num]
#     combined_list = combined_list + combined_list_new
#     print(combined_list_new)
#     j = 0
#     oshikomi = []
#     speed = []
#     while j < 3:
#         if num[j] == 1:
#             oshikomi += [random.choice((160, 220))]
#         if num[j] == 2:
#             oshikomi += [random.choice((180, 230))]
#         if num[j] == 4:
#             oshikomi += [random.choice((200, 240))]
#         j += 1
#     speed = [
#         random.choice((0.5, 1, 2)),
#         random.choice((0.5, 1, 2)),
#         random.choice((0.5, 1, 2)),
#     ]
#     k = 0
#     while k < 3:
#         print("self.oshikomi, self.speed = ", oshikomi[k], ",", speed[k])
#         k += 1
#     i += 1
# i = 0
# while i < 18:
#     print(combined_list[i], combined_list[i + 1])
#     i += 2
