# -*- coding:utf-8 -*-
#文档过滤
import re
import math
from pysqlite2 import dbapi2 as sqlite

#文档和单词
def getwords(doc):
    splitter=re.compile('\\W*')
    print doc
    # Split the words by non-alpha characters
    words=[s.lower() for s in splitter.split(doc) 
         if len(s)>2 and len(s)<20]

    # Return the unique set of words only
    return dict([(w,1) for w in words])

#对分类器进行训练
class classifier:
    def __init__(self,getfeatures,filename=None):
        # 统计特征/分类组合的数量
        self.fc={}
        # 统计每个分类中的数量
        self.cc={}
        self.getfeatures=getfeatures

    def setdb(self,dbfile):
        self.con=sqlite.connect(dbfile)    
        self.con.execute('create table if not exists fc(feature,category,count)')
        self.con.execute('create table if not exists cc(category,count)')

    #增加对特征/分类组合的计数值
    def incf(self,f,cat):
        count=self.fcount(f,cat)
        if count==0:
            self.con.execute("insert into fc values ('%s','%s',1)" % (f,cat))
        else:
            self.con.execute("update fc set count=%d where feature='%s' and category='%s'" % (count+1,f,cat)) 
    #某一特征出现在某一分类中的次数
    def fcount(self,f,cat):
        res=self.con.execute('select count from fc where feature="%s" and category="%s"' % (f,cat)).fetchone()
        if res==None: return 0
        else: return float(res[0])
    #增加对某一分类的计数值
    def incc(self,cat):
        count=self.catcount(cat)
        if count==0:
            self.con.execute("insert into cc values ('%s',1)" % (cat))
        else:
            self.con.execute("update cc set count=%d where category='%s'" % (count+1,cat))    
    #属于某一分类的内容项数量
    def catcount(self,cat):
        res=self.con.execute('select count from cc where category="%s"' % (cat)).fetchone()
        if res==None: return 0
        else: return float(res[0])
    #所有分类列表
    def categories(self):
        cur=self.con.execute('select category from cc');
        return [d[0] for d in cur]
    #所有内容项的数量
    def totalcount(self):
        res=self.con.execute('select sum(count) from cc').fetchone();
        if res==None: return 0
        return res[0]

    def train(self,item,cat):
        features=self.getfeatures(item)
        # 针对该分类为每个特征增加计数值
        for f in features:
            self.incf(f,cat)
        # 增加针对该分类的计数值
        self.incc(cat)
        self.con.commit()
#测试分类器
cl=classifier(getwords)
cl.setdb('classifier.db')
cl.train('the quick brown fox jumps over the lazy dog','good')
cl.train('make quick money in the online casino','bad')
print cl.fcount('quick','good')
