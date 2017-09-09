# -*- coding:utf-8 -*-
#智能进化-遗传算法
from random import random,randint,choice
from copy import deepcopy
from math import log

#构造树状程序
#封装类：对应节点上的函数
class fwrapper:
  def __init__(self,function,childcount,name):
    self.function=function
    self.childcount=childcount
    self.name=name

#带子节点的节点：对应函数型节点
class node:
  def __init__(self,fw,children):
    self.function=fw.function
    self.name=fw.name
    self.children=children

  def evaluate(self,inp):    
    results=[n.evaluate(inp) for n in self.children]
    return self.function(results)
  
  def display(self,indent=0):
    print (' '*indent)+self.name
    for c in self.children:
      c.display(indent+1)
    
#返回传递给程序的参数
class paramnode:
  def __init__(self,idx):
    self.idx=idx

  def evaluate(self,inp):
    return inp[self.idx]
  
  def display(self,indent=0):
    print '%sp%d' % (' '*indent,self.idx)
    
#返回常量值的节点    
class constnode:
  def __init__(self,v):
    self.v=v
    
  def evaluate(self,inp):
    return self.v
  
  def display(self,indent=0):
    print '%s%d' % (' '*indent,self.v)
    
#针对节点的操作函数
addw=fwrapper(lambda l:l[0]+l[1],2,'add')
subw=fwrapper(lambda l:l[0]-l[1],2,'subtract') 
mulw=fwrapper(lambda l:l[0]*l[1],2,'multiply')

def iffunc(l):
  if l[0]>0: return l[1]
  else: return l[2]
ifw=fwrapper(iffunc,3,'if')

def isgreater(l):
  if l[0]>l[1]: return 1
  else: return 0
gtw=fwrapper(isgreater,2,'isgreater')

flist=[addw,mulw,ifw,gtw,subw]

def exampletree():
  return node(ifw,[
                  node(gtw,[paramnode(0),constnode(3)]),
                  node(addw,[paramnode(1),constnode(5)]),
                  node(subw,[paramnode(1),constnode(2)]),
                  ]
              )

#测试树状程序
"""
tree=exampletree()
print tree.evaluate([2,3])
print tree.evaluate([6,90])
"""
#测试显示程序
"""
tree=exampletree()
tree.display()
"""
#构造初始种群
"""
pc:所需输入参数的个数
maxdepth:树的最大深度
fpr:新建节点属于函数型节点的概率
ppr:新建节点属于paramnode节点的概率
"""
def makerandomtree(pc,maxdepth=4,fpr=0.5,ppr=0.6):
  if random()<fpr and maxdepth>0:
    f=choice(flist)
    children=[makerandomtree(pc,maxdepth-1,fpr,ppr) for i in range(f.childcount)]
    return node(f,children)
  elif random()<ppr:
    return paramnode(randint(0,pc-1))
  else:
    return constnode(randint(0,10))

#测试初始种群
"""
random1=makerandomtree(2)
print random1.evaluate([7,1])
print random1.evaluate([2,4])
random1.display()
print('----------------')
random2=makerandomtree(2)
print random2.evaluate([5,3])
print random2.evaluate([5,20])
random2.display()
"""

def hiddenfunction(x,y):
    return x**2+2*y+3*x+5

def buildhiddenset():
  rows=[]
  for i in range(200):
    x=randint(0,40)
    y=randint(0,40)
    rows.append([x,y,hiddenfunction(x,y)])
  return rows

def scorefunction(tree,s):
  dif=0
  for data in s:
    v=tree.evaluate([data[0],data[1]])
    dif+=abs(v-data[2])
  return dif
#测试衡量程序的好坏
"""
hiddenset=buildhiddenset()
random1=makerandomtree(2)
random2=makerandomtree(2)
print scorefunction(random2,hiddenset)
print scorefunction(random1,hiddenset)
"""
#变异
def mutate(t,pc,probchange=0.1):
  if random()<probchange:
    return makerandomtree(pc)
  else:
    result=deepcopy(t)
    if hasattr(t,"children"):
      result.children=[mutate(c,pc,probchange) for c in t.children]
    return result
#测试变异
"""
hiddenset=buildhiddenset()
random1=makerandomtree(2)
random1.display()
muttree=mutate(random1,2)
muttree.display()
print scorefunction(random1,hiddenset)
print scorefunction(muttree,hiddenset)
"""
#交叉
def crossover(t1,t2,probswap=0.7,top=1):
  if random()<probswap and not top:
    return deepcopy(t2) 
  else:
    result=deepcopy(t1)
    if hasattr(t1,'children') and hasattr(t2,'children'):
      result.children=[crossover(c,choice(t2.children),probswap,0) 
                       for c in t1.children]
    return result

#测试交叉
"""
hiddenset=buildhiddenset()
random1=makerandomtree(2)
random1.display()
print('-------------------')
random2=makerandomtree(2)
random2.display()
print('-------------------')
cross=crossover(random1,random2)
cross.display()
"""
   
#构筑环境
def evolve(pc,popsize,rankfunction,maxgen=500,
           mutationrate=0.1,breedingrate=0.4,pexp=0.7,pnew=0.05):
  # 返回一个较小的随机数
  # pexp取值越小，取得的随机数越小
  def selectindex():
    return int(log(random())/log(pexp))

  # 创建一个随机的初始种群
  population=[makerandomtree(pc) for i in range(popsize)]
  for i in range(maxgen):
    scores=rankfunction(population)
    print scores[0][0]
    if scores[0][0]==0: break
    
    # 得到两个最优的程序
    newpop=[scores[0][1],scores[1][1]]
    
    # 构造下一代
    while len(newpop)<popsize:
      if random()>pnew:
        newpop.append(mutate(
                      crossover(scores[selectindex()][1],
                                 scores[selectindex()][1],
                                probswap=breedingrate),
                        pc,probchange=mutationrate))
      else:
      # 加入一个随机节点，以增加种群的多样性
        newpop.append(makerandomtree(pc))
        
    population=newpop
  scores[0][1].display()    
  return scores[0][1]

#根据scorefunction结果进行排序
def getrankfunction(dataset):
  def rankfunction(population):
    scores=[(scorefunction(t,dataset),t) for t in population]
    scores.sort()
    return scores
  return rankfunction

#测试自动生成数学公式
rf=getrankfunction(buildhiddenset())
print evolve(2,500,rf,mutationrate=0.2,breedingrate=0.1,pexp=0.7,pnew=0.1)