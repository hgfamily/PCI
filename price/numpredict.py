# -*- encoding: utf-8 -*-
#构建价格模型
from random import random,randint
import math

#对葡萄酒价格建模
def wineprice(rating,age):
    peak_age=rating-50

    # 根据等级来计算价格
    price=rating/2
    if age>peak_age:
        # 经过‘峰值年’，后继5年里其品质会变差
        price=price*(5-(age-peak_age)/2)
    else:
        # 价格在接近‘峰值年’时会增加到原值的5倍
        price=price*(5*((age+1)/peak_age))
    if price<0: price=0
    return price

#构造葡萄酒价格数据集
def wineset1():
    rows=[]
    for i in range(300):
        # 随机生成等级和年代
        rating=random()*50+50
        age=random()*50

        # 获取参考价格
        price=wineprice(rating,age)

        # 添加噪声
        price*=(random()*0.2+0.8)

        # 加入数据集
        rows.append({'input':(rating,age),
                 'result':price})
    return rows

#测试数据集
"""
data=wineset1()
print data[0]
print data[1]
"""
#KNN最近邻算法
#定义相似度
def euclidean(v1,v2):
    d=0.0
    for i in range(len(v1)):
        d+=(v1[i]-v2[i])**2
    return math.sqrt(d)

#测试相似度
"""
data=wineset1()
print data[0]['input']
print data[1]['input']
print euclidean(data[0]['input'],data[1]['input'])
"""

def getdistances(data,vec1):
    distancelist=[]
    # 循环遍历数据集中的每一项
    for i in range(len(data)):
        vec2=data[i]['input']
        # 添加距离与索引
        distancelist.append((euclidean(vec1,vec2),i))
    # 按距离排序
    distancelist.sort()
    return distancelist

#前k项平均值
def knnestimate(data,vec1,k=5):
    # 获得经过排序的距离值
    dlist=getdistances(data,vec1)
    avg=0.0

    # 对前k项结果求平均
    for i in range(k):
        idx=dlist[i][1]
        avg+=data[idx]['result']
    avg=avg/k
    return avg
#测试对新商品进行估价
"""
data=wineset1()
print knnestimate(data,(95.0,3.0))
print knnestimate(data,(99.0,3.0))
print('---------------')
print knnestimate(data,(99.0,5.0))
print wineprice(99.0,5.0)#得到实际价格
print knnestimate(data,(99.0,5.0),k=2)#尝试更少的近邻
"""
#为近邻分配权重-3种方法
#反函数
def inverseweight(dist,num=1.0,const=0.1):
    return num/(dist+const)
#减法函数
def subtractweight(dist,const=1.0):
    if dist>const: 
        return 0
    else: 
        return const-dist
#高斯函数
def gaussian(dist,sigma=5.0):
    return math.e**(-dist**2/(2*sigma**2))

#加权knn
def weightedknn(data,vec1,k=5,weightf=gaussian):
    # 得到距离值
    dlist=getdistances(data,vec1)
    avg=0.0
    totalweight=0.0

    # 得到加权平均值
    for i in range(k):
        dist=dlist[i][0]
        idx=dlist[i][1]
        weight=weightf(dist)
        avg+=weight*data[idx]['result']
        totalweight+=weight
    if totalweight==0: return 0
    avg=avg/totalweight
    return avg

#交叉验证-选择正确的参数
def dividedata(data,test=0.05):
    trainset=[]
    testset=[]
    for row in data:
        if random()<test:
            testset.append(row)
        else:
            trainset.append(row)
    return trainset,testset

def testalgorithm(algf,trainset,testset):
    error=0.0
    for row in testset:
        guess=algf(trainset,row['input'])
        error+=(row['result']-guess)**2
    return error/len(testset)

#不同参数值的误差情况
def crossvalidate(algf,data,trials=100,test=0.1):
    error=0.0
    for i in range(trials):
        trainset,testset=dividedata(data,test)
        error+=testalgorithm(algf,trainset,testset)
    return error/trials

def knn3(d,v):
    return knnestimate(d,v,k=3)

def knn1(d,v):
    return knnestimate(d,v,k=1)

def knninverse(d,v):
    return weightedknn(d,v,weightf=inverseweight)

def knnsubtract(d,v):
    return weightedknn(d,v,weightf=subtractweight)
#测试knnestimate函数中不同k值的误差情况
"""
print('测试knnestimate函数中不同k值的误差情况:')
data=wineset1()
print('k=5:')
print crossvalidate(knnestimate,data)
print('k=3')
print crossvalidate(knn3,data)
print('k=1')
print crossvalidate(knn1,data)
#测试加权knn函数中不同权重函数的误差情况
print('测试加权knn函数中不同权重函数的误差情况:')
print('高斯函数:')
print crossvalidate(weightedknn,data)
print('反函数:')
print crossvalidate(knninverse,data)
print('减法函数:')
print crossvalidate(knnsubtract,data)
"""
#不同类型的变量
#带有通道信息和酒瓶尺寸的新数据集
def wineset2():
    rows=[]
    for i in range(300):
        rating=random()*50+50
        age=random()*50
        aisle=float(randint(1,20))#通道号
        bottlesize=[375.0,750.0,1500.0][randint(0,2)]#酒瓶尺寸
        price=wineprice(rating,age)
        price*=(bottlesize/750)
        price*=(random()*0.2+0.9)
        rows.append({'input':(rating,age,aisle,bottlesize),'result':price})
    return rows

#测试新数据集对knn的影响情况
"""
data=wineset2()
print crossvalidate(knn3,data)
print crossvalidate(weightedknn,data)
"""
#按比例缩放
def rescale(data,scale):
    scaleddata=[]
    for row in data:
        scaled=[scale[i]*row['input'][i] for i in range(len(scale))]
        scaleddata.append({'input':scaled,'result':row['result']})
    return scaleddata

#测试缩放结果
"""
data=wineset2()
sdata=rescale(data,[5,5,0.1,10])
print crossvalidate(knn3,sdata)
print crossvalidate(weightedknn,sdata)
"""
#优化缩放结果
#成本函数
def createcostfunction(algf,data):
    def costf(scale):
        sdata=rescale(data,scale)
        return crossvalidate(algf,sdata,trials=20)
    return costf

weightdomain=[(0,10)]*4

import optimization
#测试优化缩放结果
"""
#退火优化算法
data=wineset2()
costf=createcostfunction(knnestimate,data)
print optimization.annealingoptimize(weightdomain,costf,step=2)
#遗传优化算法
print optimization.geneticoptimize(weightdomain,costf,popsize=5,mutprob=1,elite=4,maxiter=20)
"""
#不对称分布
def wineset3():
    rows=wineset1()
    for row in rows:
        if random()<0.5:
            # 葡萄酒从折扣店购得
            row['result']*=0.5
    return rows
#测试不对称分布-购买源不同
"""
data=wineset3()
print wineprice(99.0,20.0)
print weightedknn(data,[99.0,20.0])
"""
#估计概率密度
def probguess(data,vec1,low,high,k=5,weightf=gaussian):
    dlist=getdistances(data,vec1)
    nweight=0.0
    tweight=0.0
    
    for i in range(k):
        dist=dlist[i][0]
        idx=dlist[i][1]
        weight=weightf(dist)
        v=data[idx]['result']

        # 判断当前数据点是否位于指定范围内
        if v>=low and v<=high:
            nweight+=weight
        tweight+=weight
    if tweight==0: return 0

    # 概率等于位于指定范围内的权重值除以所有权重值
    return nweight/tweight
#测试估计概率密度
"""
data=wineset3()
print probguess(data,[99.0,20.0],40,80)
print probguess(data,[99.0,20.0],80,120)
print probguess(data,[99.0,20.0],120,1000)
print probguess(data,[99.0,20.0],30,120)
"""
from pylab import *
"""
a=array([1,2,3,4])
b=array([4,2,3,1])
plot(a,b)
show()
t1=arange(0.0,10.0,0.1)
plot(t1,sin(t1))
show()
"""
#累积概率
def cumulativegraph(data,vec1,high,k=5,weightf=gaussian):
    t1=arange(0.0,high,0.1)
    cprob=array([probguess(data,vec1,0,v,k,weightf) for v in t1])
    plot(t1,cprob)
    show()

#测试绘制累积概率图
"""
data=wineset3()
cumulativegraph(data,(1,1),120)
"""
#绘制实际概率图
def probabilitygraph(data,vec1,high,k=5,weightf=gaussian,ss=5.0):
    # 建立一个代表价格的值域范围
    t1=arange(0.0,high,0.1)

    # 得到整个值域范围内的所有概率
    probs=[probguess(data,vec1,v,v+0.1,k,weightf) for v in t1]

    # 通过加上近邻概率的高斯计算结果，对概率值做平滑处理
    smoothed=[]
    for i in range(len(probs)):
        sv=0.0
        for j in range(0,len(probs)):
            dist=abs(i-j)*0.1
            weight=gaussian(dist,sigma=ss)
            sv+=weight*probs[j]
        smoothed.append(sv)
    smoothed=array(smoothed)

    plot(t1,smoothed)
    show()

#测试绘制实际概率图
data=wineset3()
probabilitygraph(data,(1,1),120)