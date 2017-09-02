# -*- coding:utf-8 -*-
#文档过滤-使用字典
import re
import math

def sampletrain(cl):
    cl.train('Nobody owns the water.','good')
    cl.train('the quick rabbit jumps fences','good')
    cl.train('buy pharmaceuticals now','bad')
    cl.train('make quick money at the online casino','bad')
    cl.train('the quick brown fox jumps','good')
#文档和单词
def getwords(doc):
    splitter=re.compile('\\W*')
    # 根据非字母字符进行单词划分
    words=[s.lower() for s in splitter.split(doc) 
         if len(s)>2 and len(s)<20]

    # 只返回一组不重复的单词
    return dict([(w,1) for w in words])

#对分类器进行训练
class classifier:
    def __init__(self,getfeatures,filename=None):
        # 统计特征/分类组合的数量
        self.fc={}
        # 统计每个分类中的数量
        self.cc={}
        self.getfeatures=getfeatures
    
    #增加对特征/分类组合的计数值
    def incf(self,f,cat):
        self.fc.setdefault(f,{})
        self.fc[f].setdefault(cat,0)
        self.fc[f][cat]+=1
    
    #某一特征出现在某一分类中的次数
    def fcount(self,f,cat):
        if f in self.fc and cat in self.fc[f]:
            return float(self.fc[f][cat])
        return 0.0
    
    #增加对某一分类的计数值
    def incc(self,cat):
        self.cc.setdefault(cat,0)
        self.cc[cat]+=1
    
    #属于某一分类的内容项数量
    def catcount(self,cat):
        if cat in self.cc:
            return float(self.cc[cat])
        return 0
        
    #所有分类列表
    def categories(self):
        return self.cc.keys()
    
    #所有内容项的数量
    def totalcount(self):
        return sum(self.cc.values())


    def train(self,item,cat):
        features=self.getfeatures(item)
        # 针对该分类为每个特征增加计数值
        for f in features:
            self.incf(f,cat)
        # 增加针对该分类的计数值
        self.incc(cat)

    def fprob(self,f,cat):
        if self.catcount(cat)==0: return 0

        # 特征在分类中出现的总次数，除以分类中包含的内容项总数
        return self.fcount(f,cat)/self.catcount(cat)
    
    def weightedprob(self,f,cat,prf,weight=1.0,ap=0.5):
        # 计算当前概率值
        basicprob=prf(f,cat)

       #统计特征在所有分钟中出现的次数
        totals=sum([self.fcount(f,c) for c in self.categories()])

        # 计算加权平均
        bp=((weight*ap)+(totals*basicprob))/(weight+totals)
        return bp    

#测试分类器
"""
cl=classifier(getwords)
cl.train('the quick brown fox jumps over the lazy dog','good')
cl.train('make quick money in the online casino','bad')
print cl.fcount('quick','good')
print cl.fcount('quick','bad')
sampletrain(cl)
print cl.fcount('quick','bad')
"""
#测试概率
"""
cl=classifier(getwords)
sampletrain(cl)
print cl.fprob('quick','good')
"""
#测试加权平均概率
"""
cl=classifier(getwords)
sampletrain(cl)
print cl.weightedprob('money','good',cl.fprob)
"""

#朴素贝叶斯分类器-针对整篇文档的概率Pr(category|document)
class naivebayes(classifier):

    def __init__(self,getfeatures):
        classifier.__init__(self,getfeatures)
        self.thresholds={}

    def docprob(self,item,cat):
        features=self.getfeatures(item)   

        # 将所有特征的概率相乘
        p=1
        for f in features: p*=self.weightedprob(f,cat,self.fprob)
        return p

    def prob(self,item,cat):
        catprob=self.catcount(cat)/self.totalcount()
        docprob=self.docprob(item,cat)
        return docprob*catprob
    
    #设置阈值
    def setthreshold(self,cat,t):
        self.thresholds[cat]=t

    def getthreshold(self,cat):
        if cat not in self.thresholds: return 1.0
        return self.thresholds[cat]

    def classify(self,item,default=None):
        probs={}
        # 寻找概率最大的分类
        max=0.0
        for cat in self.categories():
            probs[cat]=self.prob(item,cat)
            if probs[cat]>max: 
                max=probs[cat]
                best=cat

        # 确保概率值超出 次大概率值*阈值
        for cat in probs:
            if cat==best: continue
            if probs[cat]*self.getthreshold(best)>probs[best]: return default
        return best

#测试朴素贝叶斯分类器
"""
cl=naivebayes(getwords)
sampletrain(cl)
print cl.prob('quick rabbit','good')
print cl.prob('buy','bad')
"""
#测试阈值
"""
cl=naivebayes(getwords)
sampletrain(cl)
print cl.classify('quick rabbit',default='unknown')
print cl.classify('quick money',default='unknown')
cl.setthreshold('bad',3.0)
print cl.classify('quick money',default='unknown')
for i in range(10):
    sampletrain(cl)
print cl.classify('quick money',default='unknown')
"""
#费舍尔方法-针对特征的分类概率Pr(category|feature)
class fisherclassifier(classifier):
    def cprob(self,f,cat):
        # 特征在该分类中出现的频率   
        clf=self.fprob(f,cat)
        if clf==0: return 0

        # 特征在所有分类中出现的频率
        freqsum=sum([self.fprob(f,c) for c in self.categories()])

        # 概率等于特征在该分类中出现的频率除以总体频率
        p=clf/(freqsum)

        return p
    
    def fisherprob(self,item,cat):
        # 将所有概率相乘
        p=1
        features=self.getfeatures(item)
        for f in features:
            p*=(self.weightedprob(f,cat,self.cprob))

        # 取自然对数，并乘以-2
        fscore=-2*math.log(p)

        # 利用倒置对数卡方函数求得概率
        return self.invchi2(fscore,len(features)*2)
    
    def invchi2(self,chi, df):
        m = chi / 2.0
        sum = term = math.exp(-m)
        for i in range(1, df//2):
            term *= m / i
            sum += term
        return min(sum, 1.0)
    
    #对内容项进行分类,设置分类的下限值
    def __init__(self,getfeatures):
        classifier.__init__(self,getfeatures)
        self.minimums={}

    def setminimum(self,cat,min):
        self.minimums[cat]=min

    def getminimum(self,cat):
        if cat not in self.minimums: return 0
        return self.minimums[cat]
    def classify(self,item,default=None):
        # 循环遍历并寻找最佳结果
        best=default
        max=0.0
        for c in self.categories():
            p=self.fisherprob(item,c)
            # 确保其超过分类的下限值
            if p>self.getminimum(c) and p>max:
                best=c
                max=p
        return best

#测试费舍尔方法
#分类概率
"""
cl=fisherclassifier(getwords)
sampletrain(cl)
print cl.cprob('quick','good')
print cl.cprob('money','bad')
print cl.weightedprob('money','bad',cl.cprob)
"""
#组合概率
"""
cl=fisherclassifier(getwords)
sampletrain(cl)
print cl.cprob('quick','good')
print cl.fisherprob('quick rabbit','good')
print cl.fisherprob('quick rabbit','bad')
"""
#对内容项进行分类
cl=fisherclassifier(getwords)
sampletrain(cl)
print cl.classify('quick rabbit')
print cl.classify('quick money')
print('设置分类的下限值:')
cl.setminimum('bad',0.8)
print cl.classify('quick money')
cl.setminimum('good',0.4)
print cl.classify('quick money')