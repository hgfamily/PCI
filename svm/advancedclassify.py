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
avgs=lineartrain(agesonly)
print dpclassify([48,20],avgs)

def yesno(v):
    if v=='yes': return 1
    elif v=='no': return -1
    else: return 0

def matchcount(interest1,interest2):
    l1=interest1.split(':')
    l2=interest2.split(':')
    x=0
    for v in l1:
        if v in l2: x+=1
    return x

def loadnumerical():
    oldrows=loadmatch('matchmaker.csv')
    newrows=[]
    for row in oldrows:
        d=row.data
        data=[float(d[0]),yesno(d[1]),yesno(d[2]),
          float(d[5]),yesno(d[6]),yesno(d[7]),
          matchcount(d[3],d[8]),
          milesdistance(d[4],d[9]),
          row.match]
        newrows.append(matchrow(data))
    return newrows
