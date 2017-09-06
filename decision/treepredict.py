# -*- coding:utf-8 -*-
#预测注册用户的行为
from PIL import Image,ImageDraw

my_data=[['slashdot','USA','yes',18,'None'],
         ['google','France','yes',23,'Premium'],
        ['digg','USA','yes',24,'Basic'],
        ['kiwitobes','France','yes',23,'Basic'],
        ['google','UK','no',21,'Premium'],
        ['(direct)','New Zealand','no',12,'None'],
        ['(direct)','UK','no',21,'Basic'],
        ['google','USA','no',24,'Premium'],
        ['slashdot','France','yes',19,'None'],
        ['digg','USA','no',18,'None'],
        ['google','UK','no',18,'None'],
        ['kiwitobes','UK','no',19,'None'],
        ['digg','New Zealand','yes',12,'Basic'],
        ['slashdot','UK','no',21,'None'],
        ['google','UK','yes',18,'Basic'],
        ['kiwitobes','France','yes',19,'Basic']]

class decisionnode:
    def __init__(self,col=-1,value=None,results=None,tb=None,fb=None):
        self.col=col
        self.value=value
        self.results=results
        self.tb=tb
        self.fb=fb

# 在某一列上堆数据集合进行拆开，能够处理数值型数据或名词性数据
def divideset(rows,column,value):
    # 定义函数说明数据属于第一组还是第二组
    split_function=None
    if isinstance(value,int) or isinstance(value,float):
        split_function=lambda row:row[column]>=value
    else:
        split_function=lambda row:row[column]==value

    # 将数据集拆分成两个集合并返回
    set1=[row for row in rows if split_function(row)]
    set2=[row for row in rows if not split_function(row)]
    return (set1,set2)

#对结果进行计数
def uniquecounts(rows):
    results={}
    for row in rows:
        r=row[len(row)-1]
        if r not in results: results[r]=0
        results[r]+=1
    return results

# 基尼不纯度函数---随机放置的数据项出现于错误分类中的概率
def giniimpurity(rows):
    total=len(rows)
    counts=uniquecounts(rows)
    imp=0
    for k1 in counts:
        p1=float(counts[k1])/total
        for k2 in counts:
            if k1==k2: continue
            p2=float(counts[k2])/total
            imp+=p1*p2
    return imp

# 熵是遍历所有的结果之后所得到的p(x)log(p(x))之和
def entropy(rows):
    from math import log
    log2=lambda x:log(x)/log(2)  
    results=uniquecounts(rows)
    # 开始计算熵值
    ent=0.0
    for r in results.keys():
        p=float(results[r])/len(rows)
        ent=ent-p*log2(p)
    return ent

#测试基尼不纯度与熵值
"""
print giniimpurity(my_data)
print entropy(my_data)
set1,set2=divideset(my_data,2,'yes')
print giniimpurity(set1)
print entropy(set1)
"""

#递归方式构造树
def buildtree(rows,scoref=entropy):
    if len(rows)==0: return decisionnode()
    current_score=scoref(rows)

    # 定义变量记录最佳拆分条件
    best_gain=0.0
    best_criteria=None
    best_sets=None

    column_count=len(rows[0])-1
    for col in range(0,column_count):
        # 在当前列中生成一个由不同值构成的序列
        column_values={}
        for row in rows:
            column_values[row[col]]=1
        # 根据列中每个值，对数据集进行拆分
        for value in column_values.keys():
            (set1,set2)=divideset(rows,col,value)

            # 信息增益
            p=float(len(set1))/len(rows)
            gain=current_score-p*scoref(set1)-(1-p)*scoref(set2)
            if gain>best_gain and len(set1)>0 and len(set2)>0:
                best_gain=gain
                best_criteria=(col,value)
                best_sets=(set1,set2)
    # 创建子分支 
    if best_gain>0:
        trueBranch=buildtree(best_sets[0])
        falseBranch=buildtree(best_sets[1])
        return decisionnode(col=best_criteria[0],value=best_criteria[1],
                        tb=trueBranch,fb=falseBranch)
    else:
        return decisionnode(results=uniquecounts(rows))

#显示决策树
def printtree(tree,indent=''):
    # 判断是否叶节点
    if tree.results!=None:
        print str(tree.results)
    else:
        # 打印判断条件
        print str(tree.col)+':'+str(tree.value)+'? '

        # 打印分支
        print indent+'T->',
        printtree(tree.tb,indent+'  ')
        print indent+'F->',
        printtree(tree.fb,indent+'  ')

#测试决策树的构造与显示
"""
tree=buildtree(my_data)
printtree(tree)
"""

def getwidth(tree):
    if tree.tb==None and tree.fb==None: return 1
    return getwidth(tree.tb)+getwidth(tree.fb)

def getdepth(tree):
    if tree.tb==None and tree.fb==None: return 0
    return max(getdepth(tree.tb),getdepth(tree.fb))+1

def drawtree(tree,jpeg='tree.jpg'):
    w=getwidth(tree)*100
    h=getdepth(tree)*100+120

    img=Image.new('RGB',(w,h),(255,255,255))
    draw=ImageDraw.Draw(img)

    drawnode(draw,tree,w/2,20)
    img.save(jpeg,'JPEG')

def drawnode(draw,tree,x,y):
    if tree.results==None:
        # 得到每个分支的宽度
        w1=getwidth(tree.fb)*100
        w2=getwidth(tree.tb)*100

        # 确定此节点所要占据的总空间
        left=x-(w1+w2)/2
        right=x+(w1+w2)/2

        # 绘制判断条件字符串
        draw.text((x-20,y-10),str(tree.col)+':'+str(tree.value),(0,0,0))

        # 绘制到分支的连线
        draw.line((x,y,left+w1/2,y+100),fill=(255,0,0))
        draw.line((x,y,right-w2/2,y+100),fill=(255,0,0))

        # 绘制分支的节点
        drawnode(draw,tree.fb,left+w1/2,y+100)
        drawnode(draw,tree.tb,right-w2/2,y+100)
    else:
        txt=' \n'.join(['%s:%d'%v for v in tree.results.items()])
        draw.text((x-20,y),txt,(0,0,0))

#测试图形方式显示决策树
"""
tree=buildtree(my_data)
drawtree(tree,jpeg='treeview.jpg')
"""
#对新的观测数据进行预测
def classify(observation,tree):
    if tree.results!=None:
        return tree.results
    else:
        v=observation[tree.col]
        branch=None
        if isinstance(v,int) or isinstance(v,float):
            if v>=tree.value: branch=tree.tb
            else: branch=tree.fb
        else:
            if v==tree.value: branch=tree.tb
            else: branch=tree.fb
        return classify(observation,branch)
#测试新的观测数据
"""
tree=buildtree(my_data)
print classify(['(direct)','USA','yes',5],tree)
"""
#剪枝
def prune(tree,mingain):
    # 如果分支不是叶节点，则进行剪枝操作
    if tree.tb.results==None:
        prune(tree.tb,mingain)
    if tree.fb.results==None:
        prune(tree.fb,mingain)
    #如果两个子分支都是叶节点，则判断他们是否需要合并
    if tree.tb.results!=None and tree.fb.results!=None:
        # 构建合并后的数据集
        tb,fb=[],[]
        for v,c in tree.tb.results.items():
            tb+=[[v]]*c
        for v,c in tree.fb.results.items():
            fb+=[[v]]*c

        # 检查熵的减少情况
        delta=entropy(tb+fb)-(entropy(tb)+entropy(fb)/2)

        if delta<mingain:
            # 合并分支
            tree.tb,tree.fb=None,None
            tree.results=uniquecounts(tb+fb)
#测试剪枝
"""
tree=buildtree(my_data)
prune(tree,0.1)
printtree(tree)
print('--------')
prune(tree,1.0)
printtree(tree)
"""
#处理缺失数据
def mdclassify(observation,tree):
    if tree.results!=None:
        return tree.results
    else:
        v=observation[tree.col]
        if v==None:
            tr,fr=mdclassify(observation,tree.tb),mdclassify(observation,tree.fb)
            tcount=sum(tr.values())
            fcount=sum(fr.values())
            tw=float(tcount)/(tcount+fcount)
            fw=float(fcount)/(tcount+fcount)
            result={}
            for k,v in tr.items(): result[k]=v*tw
            for k,v in fr.items(): result[k]=v*fw      
            return result
        else:
            if isinstance(v,int) or isinstance(v,float):
                if v>=tree.value: branch=tree.tb
                else: branch=tree.fb
            else:
                if v==tree.value: branch=tree.tb
                else: branch=tree.fb
            return mdclassify(observation,branch)

#测试处理缺失数据
"""
tree=buildtree(my_data)
print mdclassify(['google',None,'yes',None],tree)
print mdclassify(['google','France',None,None],tree)
"""