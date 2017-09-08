# -*- coding:utf-8 -*-
#寻找独立特征
import feedparser
import re
from nmf import *

feedlist=['http://www.foxnews.com/xmlfeed/rss/0,4313,0,00.rss',
          'http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml']

def stripHTML(h):
    p=''
    s=0
    for c in h:
        if c=='<': s=1
        elif c=='>':
            s=0
            p+=' '
        elif s==0: p+=c
    return p


def separatewords(text):
    splitter=re.compile('\\W*')
    return [s.lower() for s in splitter.split(text) if len(s)>3]

#处理下载数据
def getarticlewords():
    allwords={}#单词在所有文章中被使用的次数，作为特征提取的判断依据
    articlewords=[]#单词在每篇文章中出现的次数
    articletitles=[]#文章列表的标题
    ec=0
    # 遍历每个订阅源
    for feed in feedlist:
        f=feedparser.parse(feed)

        # 遍历每篇文章
        for e in f.entries:
            # 跳过标题相同的文章
            if e.title in articletitles: continue

            # 提取单词
            txt=e.title.encode('utf8')+stripHTML(e.description.encode('utf8'))
            words=separatewords(txt)
            articlewords.append({})
            articletitles.append(e.title)

            # 在allwords和articlewords中增加针对当前单词的计数
            for word in words:
                allwords.setdefault(word,0)
                allwords[word]+=1
                articlewords[ec].setdefault(word,0)
                articlewords[ec][word]+=1
            ec+=1
    return allwords,articlewords,articletitles

#构造矩阵
def makematrix(allw,articlew):
    wordvec=[]
    for w,c in allw.items():
        #单词在超过3篇文章中出现过并在所有文章中出现的比例小于60%
        if c>3 and c<len(articlew)*0.6:
            wordvec.append(w) 

    # 构造单词矩阵
    l1=[[(word in f and f[word] or 0) for word in wordvec] for f in articlew]
    return l1,wordvec

#测试解析订阅源并构造矩阵
#列出单词向量中的10个单词并列出第一篇文章的标题，以及该篇文章标题在单词矩阵中出现的次数
"""
allw,artw,artt=getarticlewords()
wordmatrix,wordvec=makematrix(allw,artw)
print wordvec[0:10]
print artt[0]
print wordmatrix[0][0:10]
"""

#测试贝叶斯分类
"""
def wordmatrixfeatures(x):
    return [wordvec[w] for w in range(len(x)) if x[w]>0]

allw,artw,artt=getarticlewords()
wordmatrix,wordvec=makematrix(allw,artw)
print wordmatrixfeatures(wordmatrix[0])
import docclass
classifier=docclass.naivebayes(wordmatrixfeatures)
classifier.setdb('newtest.db')
print artt[0]
classifier.train(wordmatrix[0],'hurricane')
print artt[1]
classifier.train(wordmatrix[1],'Mexico')
print('对文章标题进行贝叶斯分类:')
print artt[2]
print classifier.classify(wordmatrix[2])
"""
#测试聚类
"""
allw,artw,artt=getarticlewords()
wordmatrix,wordvec=makematrix(allw,artw)
import clusters
clust=clusters.hcluster(wordmatrix)
clusters.drawdendrogram(clust,artt,jpeg='news.jpg')
"""
#测试非负矩阵因式分解
"""
allw,artw,artt=getarticlewords()
wordmatrix,wordvec=makematrix(allw,artw)
m1=matrix([[1,2,3],
           [4,5,6]])
m2=matrix([[1,2],[3,4],[5,6]])
w,h=factorize(m1*m2,pc=3,iter=100)
print('权重矩阵为:')
print w
print('特征矩阵为:')
print h
v=matrix(wordmatrix)
weight,feat=factorize(v,pc=20,iter=50)
print('文章矩阵的权重矩阵为:')
print weight
print('文章矩阵的特征矩阵为:')
print feat
"""
#以特征形式显示结果
from numpy import *
def showfeatures(w,h,titles,wordvec,out='features.txt'): 
    outfile=file(out,'w')  
    pc,wc=shape(h)
    toppatterns=[[] for i in range(len(titles))]
    patternnames=[]

    # 遍历所有特征
    for i in range(pc):
        slist=[]
        # 构造一个包含单词及其权重数据的列表
        for j in range(wc):
            slist.append((h[i,j],wordvec[j]))
        # 将单词列表倒序排列
        slist.sort()
        slist.reverse()

        # 打印开始的6个元素
        n=[s[1] for s in slist[0:6]]
        outfile.write(str(n)+'\n')
        patternnames.append(n)

        # 构造一个针对该特征的文章列表
        flist=[]
        for j in range(len(titles)):
            # 加入文章及其权重数据
            flist.append((w[j,i],titles[j]))
            toppatterns[j].append((w[j,i],i,titles[j]))

        # 将文章列表倒序排列
        flist.sort()
        flist.reverse()

        # 显示前3篇文章
        for f in flist[0:3]:
            outfile.write(str(f)+'\n')
        outfile.write('\n')

    outfile.close()
    # 返回模式名称
    return toppatterns,patternnames
#测试以特征形式显示结果
"""
allw,artw,artt=getarticlewords()
wordmatrix,wordvec=makematrix(allw,artw)
v=matrix(wordmatrix)
weight,feat=factorize(v,pc=20,iter=50)
topp,pn=showfeatures(weight,feat,artt,wordvec)
"""
#以文章形式显示结果
def showarticles(titles,toppatterns,patternnames,out='articles.txt'):
    outfile=file(out,'w')  

    # 遍历所有的文章
    for j in range(len(titles)):
        outfile.write(titles[j].encode('utf8')+'\n')

        # 针对该片文章，获得排位最靠前的特征并按照倒序排序
        toppatterns[j].sort()
        toppatterns[j].reverse()

        # 打印前3个模式
        for i in range(3):
            outfile.write(str(toppatterns[j][i][0])+' '+
                    str(patternnames[toppatterns[j][i][1]])+'\n')
        outfile.write('\n')

    outfile.close()

#测试以文章形式显示结果
"""
allw,artw,artt=getarticlewords()
wordmatrix,wordvec=makematrix(allw,artw)
v=matrix(wordmatrix)
weight,feat=factorize(v,pc=20,iter=50)
topp,pn=showfeatures(weight,feat,artt,wordvec)
showarticles(artt,topp,pn)
"""