# -*- encoding: utf-8 -*-
#高阶分类-核方法与svm
class matchrow:
    def __init__(self,row,allnum=False):
        if allnum:
            self.data=[float(row[i]) for i in range(len(row)-1)]
        else:
            self.data=row[0:len(row)-1]
        self.match=int(row[len(row)-1])

def loadmatch(f,allnum=False):
    rows=[]
    for line in file(f):
        rows.append(matchrow(line.split(','),allnum))
    return rows
#加载数据集
agesonly=loadmatch('agesonly.csv',allnum=True)
matchmake=loadmatch('matchmaker.csv')

from pylab import *
def plotagematches(rows):
    xdm,ydm=[r.data[0] for r in rows if r.match==1],\
      [r.data[1] for r in rows if r.match==1]
    xdn,ydn=[r.data[0] for r in rows if r.match==0],\
      [r.data[1] for r in rows if r.match==0] 

    plot(xdm,ydm,'bo')
    plot(xdn,ydn,'b+')

    show()

#线性分类器
def lineartrain(rows):
    averages={}
    counts={}

    for row in rows:
        # 得到该坐标点所属分类
        cl=row.match

        averages.setdefault(cl,[0.0]*(len(row.data)))
        counts.setdefault(cl,0)

        # 将该坐标加入averages中
        for i in range(len(row.data)):
            averages[cl][i]+=float(row.data[i])

        # 记录每个分类中有多少个坐标点
        counts[cl]+=1

    # 将总和除以计数值求得平均值
    for cl,avg in averages.items():
        for i in range(len(avg)):
            avg[i]/=counts[cl]

    return averages

def dotproduct(v1,v2):
    return sum([v1[i]*v2[i] for i in range(len(v1))])

def veclength(v):
    return sum([p**2 for p in v])

def dpclassify(point,avgs):
    b=(dotproduct(avgs[1],avgs[1])-dotproduct(avgs[0],avgs[0]))/2
    y=dotproduct(point,avgs[0])-dotproduct(point,avgs[1])+b
    if y>0: return 0
    else: return 1
    
#测试线性分类器
"""
avgs=lineartrain(agesonly)
print dpclassify([48,20],avgs)
"""

#核方法
#rbf径向基函数
def rbf(v1,v2,gamma=10):
    dv=[v1[i]-v2[i] for i in range(len(v1))]
    l=veclength(dv)
    return math.e**(-gamma*l)

def nlclassify(point,rows,offset,gamma=10):
    sum0=0.0
    sum1=0.0
    count0=0
    count1=0

    for row in rows:
        if row.match==0:
            sum0+=rbf(point,row.data,gamma)
            count0+=1
        else:
            sum1+=rbf(point,row.data,gamma)
            count1+=1
    y=(1.0/count0)*sum0-(1.0/count1)*sum1+offset

    if y>0: return 0
    else: return 1
    
def getoffset(rows,gamma=10):
    l0=[]
    l1=[]
    for row in rows:
        if row.match==0: l0.append(row.data)
        else: l1.append(row.data)
    sum0=sum(sum([rbf(v1,v2,gamma) for v1 in l0]) for v2 in l0)
    sum1=sum(sum([rbf(v1,v2,gamma) for v1 in l1]) for v2 in l1)

    return (1.0/(len(l1)**2))*sum1-(1.0/(len(l0)**2))*sum0

#测试新分类器，只考虑年龄问题，offset=0.0
"""
print nlclassify([30,30],agesonly,0.0)
print nlclassify([30,25],agesonly,0.0)
print nlclassify([25,40],agesonly,0.0)
print nlclassify([48,20],agesonly,0.0)
"""