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
    j = 0
    oshikomi = []
    speed = []
    while j < 3:
        if num[j]==1:
            oshikomi += [random.choice((150, 210))]
        if num[j]==2:
            oshikomi += [random.choice((170, 230))]
        if num[j]==4:
            oshikomi += [random.choice((190, 250))]
        j += 1
    speed = [random.choice((10, 20, 40)),random.choice((10, 20, 40)),random.choice((10, 20, 40))]
    # print("[",num1,num2,num3,"]",num)
    k = 0
    while k<3:
        print('self.number, self.oshikomi = ',oshikomi[k],',',speed[k])
        k += 1 
    i += 1
i = 0
while i<18:
    print(combined_list[i])
    i += 1