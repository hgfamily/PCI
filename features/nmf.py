# -*- coding:utf-8 -*-
#非负矩阵因式分解NMF算法：寻找特征矩阵与权重矩阵
from numpy import *

#从一组照片中自动判断出不同的面部特征
#成本函数
def difcost(a,b):
    dif=0
    for i in range(shape(a)[0]):
        for j in range(shape(a)[1]):
            # 将差值相加
            dif+=pow(a[i,j]-b[i,j],2)
    return dif

#更新特征矩阵与权重矩阵
def factorize(v,pc=10,iter=50):
    ic=shape(v)[0]
    fc=shape(v)[1]

    # 以随机值初始化权重矩阵与特征矩阵
    w=matrix([[random.random() for j in range(pc)] for i in range(ic)])
    h=matrix([[random.random() for i in range(fc)] for i in range(pc)])

    # 最多执行iter次操作
    for i in range(iter):
        wh=w*h

        # 计算当前差值
        cost=difcost(v,wh)

        if i%10==0: print cost

        # 如果矩阵已分解彻底，则立即终止
        if cost==0: break

        # 更新特征矩阵
        hn=(transpose(w)*v)
        hd=(transpose(w)*w*h)+0.000000001

        h=matrix(array(h)*array(hn)/array(hd))

        # 更新权重矩阵
        wn=(v*transpose(h))
        wd=(w*h*transpose(h))+0.000000001

        w=matrix(array(w)*array(wn)/array(wd))  

    return w,h