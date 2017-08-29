# -*- coding:utf-8 -*-
#欧几里德距离
def euclidean(p,q):
    sumSq=0.0
    
    #将差值的平方累加起来
    for i in range(len(p)):
        sumSq+=(p[i]-q[i])**2
    
    #求平方根
    return (sumSq**0.5)

p=[1,2]
q=[3,4]
print('欧几里德距离为:')
print(euclidean(p,q))

#皮尔逊相关系数
def pearson(x,y):
    n=len(x)
    vals=range(n)
    
    #简单求和
    sumx=sum([float(x[i]) for i in vals])
    sumy=sum([float(y[i]) for i in vals])
    
    #求平方和
    sumxSq=sum([x[i]**2.0 for i in vals])
    sumySq=sum([y[i]**2.0 for i in vals])
    
    #求乘积之和
    pSum=sum(x[i]*y[i] for i in vals)
    
    #计算皮尔逊评价值
    num=pSum-(sumx*sumy/n)
    den=((sumxSq-pow(sumx,2)/n)*(sumySq-pow(sumy,2)/n))**.5
    
    if den==0: return 1
    r=num/den
    return r
print('皮尔逊相关系数为:')
x=[0,1,0,3]
y=[0,1,1,1]
print(pearson(x,y))

#加权平均
def weightedmean(x,w):
    num=sum([x[i]*w[i] for i in range(len(w))])
    den=sum([w[i] for i in range(len(w))])
    return num/den

#Tanimoto系数
def tanimoto(a,b):
    c=[v for v in a if v in b]
    return (len(c))/(len(a)+len(b)-len(c))

#基尼不纯度
def giniimpurity(l):
    total=len(l)
    counts={}
    for item in l:
        counts.setdefault(item,0)
        counts[item]+=1
    
    imp=0
    for j in l:
        f1=float(counts[j])/total
        for k in l:
            if j==k:continue
            f2=float(counts[k])/total
            imp+=f1*f2
    return imp

l=['a','a','c','d','e']
print('基尼不纯度为:')
print(giniimpurity(l))

#熵
def entropy(l):
    from math import log
    log2=lambda x:log(x)/log(2)
    total=len(l)
    counts={}
    for item in l:
        counts.setdefault(titem,0)
        counts[item]+=1
    
    ent=0
    for i in counts:
        p=float(counts[i])/total
        ent-=p*log2(p)
    return ent
#方差
def variance(vals):
    mean=float(sum(vals))/len(vals)
    s=sum([(v-mean)**2 for v in vals])
    return s/len(vals)

#高斯函数
import math
def gaussian(dist,sigma=10.0):
    exp=math.e**(-dist**2/(2*sigma**2))
    return (1/(sigma*(math.pi)**.5))*exp

#点积
#利用向量中的各个元素来计算点积
def dotproduct(a,b):
    return sum([a[i]*b[i] for i in range(len(a))])

#利用夹角来计算点积
from math import acos

#计算一个向量的大小
def veclength(a):
    return sum([a[i] for i in range(len(a))])**.5
#计算两个向量间的夹角
def angle(a,b):
    dp=dotproduct(a,b)
    la=veclength(a)
    lb=veclength(b)
    costheta=dp/(la*lb)
    return acos(costheta)