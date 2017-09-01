#-*- coding:utf-8 -*-
import time
import random
import math

people = [('Seymour','BOS'),
          ('Franny','DAL'),
          ('Zooey','CAK'),
          ('Walt','MIA'),
          ('Buddy','ORD'),
          ('Les','OMA')]
destination='LGA'
flights={}
# 
for line in file('schedule.txt'):
    origin,dest,depart,arrive,price=line.strip().split(',')
    flights.setdefault((origin,dest),[])
    # Add details to the list of possible flights
    flights[(origin,dest)].append((depart,arrive,int(price)))

def getminutes(t):
    x=time.strptime(t,'%H:%M')
    return x[3]*60+x[4]

def printschedule(r):
    for d in range(len(r)/2):
        name=people[d][0]
        origin=people[d][1]
        out=flights[(origin,destination)][int(r[d])]
        ret=flights[(destination,origin)][int(r[d+1])]
        print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name,origin,
                                                  out[0],out[1],out[2],
                                                  ret[0],ret[1],ret[2])
#测试所有的航班信息
s=[1,4,3,2,7,3,6,3,2,4,5,3]
#printschedule(s)

#成本函数
def schedulecost(sol):
    totalprice=0
    latestarrival=0
    earliestdep=24*60

    for d in range(len(sol)/2):
        # 得到往程航班和返程航班
        origin=people[d][1]
        outbound=flights[(origin,destination)][int(sol[d])]
        returnf=flights[(destination,origin)][int(sol[d+1])]

        # 往返航班总价格之和
        totalprice+=outbound[2]
        totalprice+=returnf[2]

        # 记录最晚到达时间和最早离开时间
        if latestarrival<getminutes(outbound[1]): latestarrival=getminutes(outbound[1])
        if earliestdep>getminutes(returnf[0]): earliestdep=getminutes(returnf[0])

    # 每个人在机场等待直到最后一个人到达为止
    # 相同时间到达并等候返程航班
    totalwait=0  
    for d in range(len(sol)/2):
        origin=people[d][1]
        outbound=flights[(origin,destination)][int(sol[d])]
        returnf=flights[(destination,origin)][int(sol[d+1])]
        totalwait+=latestarrival-getminutes(outbound[1])
        totalwait+=getminutes(returnf[0])-earliestdep  

    # 租车时间>还车时间，则判定罚款
    if latestarrival>earliestdep: totalprice+=50

    return totalprice+totalwait

#随机搜索算法
def randomoptimize(domain,costf):
    best=999999999
    bestr=None
    for i in range(0,1000):
        # Create a random solution
        r=[float(random.randint(domain[i][0],domain[i][1])) for i in range(len(domain))]

        # Get the cost
        cost=costf(r)

        # Compare it to the best one so far
        if cost<best:
            best=cost
            bestr=r 
    return bestr

#测试随机搜索算法
"""
domain=[(0,9)]*(len(people)*2)
s=randomoptimize(domain,schedulecost)
print('测试随机搜索算法:')
print(schedulecost(s))
print(printschedule(s))
"""
#爬山法-局部范围最小值
def hillclimb(domain,costf):
    # 创建一个随机解
    sol=[random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
    while 1:
        # 创建相邻解的列表
        neighbors=[]

        for j in range(len(domain)):
            # 在每个方向上相对于原值偏离一点
            if sol[j]>domain[j][0]:
                neighbors.append(sol[0:j]+[sol[j]+1]+sol[j+1:])
            if sol[j]<domain[j][1]:
                neighbors.append(sol[0:j]+[sol[j]-1]+sol[j+1:])

        # 在相邻解中寻找最优解
        current=costf(sol)
        best=current
        for j in range(len(neighbors)):
            cost=costf(neighbors[j])
            if cost<best:
                best=cost
                sol=neighbors[j]

        # 如果没有更好的解，则退出循环
        if best==current:
            break
    return sol
#测试爬山法
domain=[(0,9)]*(len(people)*2)
s=hillclimb(domain,schedulecost)
print('测试爬山法:')
print(schedulecost(s))
printschedule(s)
#模拟退火算法-全局最小值
#可以对初始温度、冷却率和随机推进的step值进行调参
def annealingoptimize(domain,costf,T=10000.0,cool=0.85,step=1):
    # 初始化随机值
    vec=[float(random.randint(domain[i][0],domain[i][1])) for i in range(len(domain))]

    while T>0.1:
        # 选择一个索引值
        i=random.randint(0,len(domain)-1)

        # 选择一个改变索引值的方向
        dir=random.randint(-step,step)

        # 创建一个代表解的新列表，改变其中的一个值
        vecb=vec[:]
        vecb[i]+=dir
        if vecb[i]<domain[i][0]: vecb[i]=domain[i][0]
        elif vecb[i]>domain[i][1]: vecb[i]=domain[i][1]

        # 计算当前成本和新的成本
        ea=costf(vec)
        eb=costf(vecb)
        p=pow(math.e,(-eb-ea)/T)

        # 判断是否更好的解或者趋向最优解的可能的临界解
        if (eb<ea or random.random()<p):
            vec=vecb      

        # 降低温度
        T=T*cool
    return vec
#测试模拟退火算法
print('模拟退火算法:')
s=annealingoptimize(domain,schedulecost)
print(schedulecost(s))
printschedule(s)

#遗传算法
"""
可选参数：
popsize:种群大小
mutprob:变异概率
elite:允许传入下一代的部分
maxiter:运行代数
"""
def geneticoptimize(domain,costf,popsize=50,step=1,mutprob=0.2,elite=0.2,maxiter=100):
    # 变异操作
    def mutate(vec):
        i=random.randint(0,len(domain)-1)
        if domain[i][0]==domain[i][1]:
            return vec
        else:
            if random.random()<0.5 and vec[i]>domain[i][0]:
                return vec[0:i]+[vec[i]-step]+vec[i+1:] 
            else: 
                return vec[0:i]+[vec[i]+step]+vec[i+1:]

    # 交叉操作
    def crossover(r1,r2):
        i=random.randint(1,len(domain)-2)
        return r1[0:i]+r2[i:]

    # 构造初始种群
    pop=[]
    for i in range(popsize):
        vec=[random.randint(domain[i][0],domain[i][1]) 
         for i in range(len(domain))]
        pop.append(vec)

    # 每一代胜出者数
    topelite=int(elite*popsize)
 
    for i in range(maxiter):
        scores=[(costf(v),v) for v in pop]
        scores.sort()
        ranked=[v for (s,v) in scores]

        # 从纯粹的胜出者开始
        pop=ranked[0:topelite]

        # 添加变异和配对后的胜出者
        while len(pop)<popsize:
            if random.random()<mutprob:

                # 变异
                c=random.randint(0,topelite)
                pop.append(mutate(ranked[c]))
            else:

                # 交叉
                c1=random.randint(0,topelite)
                c2=random.randint(0,topelite)
                pop.append(crossover(ranked[c1],ranked[c2]))

        # 打印当前最优值
        print scores[0][0]

    return scores[0][1]

#测试遗传算法-可得出全局最优值
print('遗传算法:')
s=geneticoptimize(domain,schedulecost)
printschedule(s)