#-*- coding:utf-8 -*-
#学生宿舍优化问题

import random
import math
from optimization import *

# 每个宿舍有两个房间
dorms=['Zeus','Athena','Hercules','Bacchus','Pluto']

# 学生的首选和次选
prefs=[('Toby', ('Bacchus', 'Hercules')),
       ('Steve', ('Zeus', 'Pluto')),
       ('Karen', ('Athena', 'Zeus')),
       ('Sarah', ('Zeus', 'Pluto')),
       ('Dave', ('Athena', 'Bacchus')), 
       ('Jeff', ('Hercules', 'Pluto')), 
       ('Fred', ('Pluto', 'Athena')), 
       ('Suzie', ('Bacchus', 'Hercules')), 
       ('Laura', ('Bacchus', 'Hercules')), 
       ('James', ('Hercules', 'Athena'))]

# 题解
domain=[(0,(len(dorms)*2)-i-1) for i in range(0,len(dorms)*2)]

def printsolution(vec):
    slots=[]
    # 创建槽序列
    for i in range(len(dorms)): slots+=[i,i]

    # 遍历学生安置情况
    for i in range(len(vec)):
        x=int(vec[i])
        k=len(slots)
        if x>=k:x=k-1        
        # 从剩余槽中选择
        dorm=dorms[slots[x]]
        # 输出学生被分配的宿舍
        print prefs[i][0],dorm
        # 删除该槽
        del slots[x]

#成本函数   
def dormcost(vec):
    cost=0
    # 创建槽序列
    slots=[0,0,1,1,2,2,3,3,4,4]

    # 遍历学生安置情况
    for i in range(len(vec)):
        x=int(vec[i])
        k=len(slots)
        if x>=k:x=k-1
        dorm=dorms[slots[x]]
        pref=prefs[i][1]
        # 首选成本值为0，次选为1，其余为3
        if pref[0]==dorm: cost+=0
        elif pref[1]==dorm: cost+=1
        else: cost+=3

        # 删除该槽
        del slots[x]

    return cost

#测试学生宿舍优化问题
s=randomoptimize(domain,dormcost)
print dormcost(s)
s=geneticoptimize(domain,dormcost)
printsolution(s)