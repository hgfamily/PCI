# -*- coding:utf-8 -*-

import urllib2
from bs4 import *
from urlparse import urljoin
from pysqlite2 import dbapi2 as sqlite
import re


# Create a list of words to ignore
ignorewords={'the':1,'of':1,'to':1,'and':1,'a':1,'in':1,'is':1,'it':1}

class crawler:
    #初始化crawler类并传入数据库名称
    def __init__(self,dbname):
        self.con=sqlite.connect(dbname)
    
    def __del__(self):
        self.con.close()
    
    def dbcommit(self):
        self.con.commit()
    
    #辅助函数,用于获取条目的id,并且如果条目不存在，就将其加入数据库
    def getentryid(self,table,field,value,createnew=True):
        cur=self.con.execute(
            "select rowid from %s where %s='%s'" % (table,field,value))
        res=cur.fetchone()
        if res==None:
            cur=self.con.execute(
              "insert into %s (%s) values ('%s')" % (table,field,value))
            return cur.lastrowid
        else:
            return res[0]
    
    #为每个网页建立索引
    def addtoindex(self,url,soup):
        if self.isindexed(url): return
        print 'Indexing '+url
    
        # Get the individual words
        text=self.gettextonly(soup)
        words=self.separatewords(text)
    
        # Get the URL id
        urlid=self.getentryid('urllist','url',url)
    
        # Link each word to this url
        for i in range(len(words)):
            word=words[i]
            if word in ignorewords: continue
            wordid=self.getentryid('wordlist','word',word)
            self.con.execute("insert into wordlocation(urlid,wordid,location) values (%d,%d,%d)" % (urlid,wordid,i))
    
    #从一个Html网页中提取文字（不带标签的）
    def gettextonly(self,soup):
        v=soup.string
        if v==None:   
            c=soup.contents
            resulttext=''
            for t in c:
                subtext=self.gettextonly(t)
                resulttext+=subtext+'\n'
            return resulttext
        else:
            return v.strip()
    
    #根据任何非空白字符进行分词处理
    def separatewords(self,text):
        splitter=re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s!='']
    
    #如果url已经建过索引，则返回true
    def isindexed(self,url):
        u=self.con.execute \
            ("select rowid from urllist where url='%s'" % url).fetchone()
        if u!=None:
            #检查它是否已经被检索过了
            v=self.con.execute(
                'select * from wordlocation where urlid=%d' % u[0]).fetchone()
            if v!=None: return True
        return False
    
    #添加一个关联两个网页的链接
    def addlinkref(self,urlFrom,urlTo,linkText):
        pass
    
    #从一小组网页开始进行广度优先搜索，直至某一给定深度
    #期间为网页建立索引
    def crawl(self,pages,depth=2):
        for i in range(depth):
            newpages={}
            for page in pages:
                try:
                    c=urllib2.urlopen(page)
                except:
                    print "Could not open %s" % page
                    continue
                try:
                    soup=BeautifulSoup(c.read(),"lxml")
                    self.addtoindex(page,soup)

                    links=soup('a')
                    for link in links:
                        if ('href' in dict(link.attrs)):
                            url=urljoin(page,link['href'])
                            if url.find("'")!=-1: continue
                            url=url.split('#')[0]  # remove location portion
                            if url[0:4]=='https' and not self.isindexed(url):
                                newpages[url]=1
                            linkText=self.gettextonly(link)
                            self.addlinkref(page,url,linkText)

                    self.dbcommit()
                except:
                    print "Could not parse page %s" % page

            pages=newpages
    #创建数据库表
    def createindextables(self):
        self.con.execute('create table urllist(url)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid,wordid,location)')
        self.con.execute('create table link(fromid integer,toid integer)')
        self.con.execute('create table linkwords(wordid,linkid)')
        self.con.execute('create index wordidx on wordlist(word)')
        self.con.execute('create index urlidx on urllist(url)')
        self.con.execute('create index wordurlidx on wordlocation(wordid)')
        self.con.execute('create index urltoidx on link(toid)')
        self.con.execute('create index urlfromidx on link(fromid)')
        self.dbcommit()
#测试urllib2
"""
c=urllib2.urlopen('https://bytes.com/about_us.html')
contents=c.read()
print(contents[0:10])
"""
#测试crawl
"""
pagelist=['https://bytes.com/about_us.html']
crawler=crawler('')
crawler.crawl(pagelist)
"""
"""
#建立searchindex.db数据库
print("建立searchindex.db数据库")
crawler=crawler('searchindex.db')
crawler.createindextables()
print("-----------------------")
"""
#为网页建立索引
crawler=crawler('searchindex.db')
pages=['https://bytes.com/about_us.html']
crawler.crawl(pages)
