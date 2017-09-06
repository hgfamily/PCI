# -*- encoding: utf-8 -*-
#向用户提供商品-协作型过滤技术
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 
 'You, Me and Dupree': 3.5}, 
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0, 
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0}, 
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}

from math import sqrt

#基于用户的协作型过滤
#欧几里德距离评价
#返回一个有关person1与person2的基于距离的相似度评价
def sim_distance(prefs,person1,person2):
    #得到双方都曾评价过的物品列表
    si={}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item]=1
    
    #如果两者没有共同之处，返回0
    if len(si)==0:return 0
    
    #计算所有差值的平方和
    sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2)
                        for item in prefs[person1] if item in prefs[person2]])
    
    return 1/(1+sqrt(sum_of_squares))

#测试
#print(sim_distance(critics,'Toby','Gene Seymour'))
print('欧几里德距离评价:')
for p in list(critics):
    for k in list(critics):
        if p==k:continue
        print('{0} and {1} 相似度评价值为 {2}'.format(p,k,sim_distance(critics,p,k)))
    print('#############')

#皮尔逊相关度评价
#返回p1与p2的皮尔逊相关系数
def sim_pearson(prefs,p1,p2):
    #得到双方都曾评价过的物品列表
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item]=1
    
    n=len(si)
    
    if n==0:return 1
    
    #对所有偏好求和
    sum1=sum([prefs[p1][it] for it in si])
    sum2=sum([prefs[p2][it] for it in si])
    
    #求平方和
    sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq=sum([pow(prefs[p2][it],2) for it in si])
    
    #求乘积之和
    pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])
    
    #计算皮尔逊评价值
    num=pSum-(sum1*sum2)/n
    den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    
    if den==0:return 1
    r=num/den
    return r

print('皮尔逊相关度评价:')
print(sim_pearson(critics,'Lisa Rose','Gene Seymour'))
print('#############')

#从反映偏好的字典中返回最匹配者
#返回结果的个数和相似度函数均为可选参数
def topMatches(prefs,person,n=5,similarity=sim_pearson):
    scores=[(similarity(prefs,person,other),other) for other in prefs if other!=person]
    #对列表进行排序，评价值最高者排在最前面
    scores.sort()
    scores.reverse()
    return scores[0:n]

print('为评论者打分:')
print(topMatches(critics,'Toby',n=3))
print('###############')

#推荐物品
#利用所有他人评价值的加权平均，为某人提供建议
def getRecommendations(prefs,person,similarity=sim_pearson):
    totals={}
    simSums={}
    for other in prefs:
        if other==person:continue
        sim=similarity(prefs,person,other)
        if sim<=0:continue
        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item]==0:
                #相似度*评价值
                totals.setdefault(item,0)
                totals[item]+=prefs[other][item]*sim
                #相似度之和
                simSums.setdefault(item,0)
                simSums[item]+=sim
    #建立一个归一化的列表
    rankings=[(total/simSums[item],item) for item,total in totals.items()]
    #返回经过排序的列表
    rankings.sort()
    rankings.reverse()
    return rankings

print('利用所有他人评价值的加权平均，为某人提供建议:')
print(getRecommendations(critics,'Toby'))
print(getRecommendations(critics,'Toby',similarity=sim_distance))
print('###############')

#匹配商品
#转换函数
def transformPrefs(prefs):
    result={}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
            
            #将物品与人员对调
            result[item][person]=prefs[person][item]
    return result

print('得到一组与《Superman Returns》最为相近的影片:')
movies=transformPrefs(critics)
print(topMatches(movies,'Superman Returns'))
print('邀请谁和自己一起参加某部影片的首映式:')
print(getRecommendations(movies,'Just My Luck'))
print('###############')

#基于物品的协作型过滤
#构造物品比较数据集
def calculateSimilarItems(prefs,n=10):
    result={}
    itemPrefs=transformPrefs(prefs)
    c=0
    for item in itemPrefs:
        c+=1
        if c%100==0: print '%d / %d' % (c,len(itemPrefs))
        #寻找最为相近的物品
        scores=topMatches(itemPrefs,item,n=n,similarity=sim_distance)
        result[item]=scores
    return result

print('*******************')
print('构造物品相似度的数据集:')
itemsim=calculateSimilarItems(critics)
print(itemsim)
print('*******************')

#获得推荐
def getRecommendedItems(prefs,itemMatch,user):
    userRatings=prefs[user]
    scores={}
    totalSim={}
    
    #循环遍历由当前用户评分的物品
    for (item,rating) in userRatings.items():
        #循环遍历与当前物品相近的物品
        for (similarity,item2) in itemMatch[item]:
            if item2 in userRatings:continue
            #评价值与相似度的加权之和
            scores.setdefault(item2,0)
            scores[item2]+=similarity*rating
            #全部相似度之和
            totalSim.setdefault(item2,0)
            totalSim[item2]+=similarity
        
    rangkings=[(scores/totalSim[item],item) for item,scores in scores.items()]
    rangkings.sort()
    rangkings.reverse()
    return rangkings

print('为Toby提供一个新的推荐结果:')
print(getRecommendedItems(critics,itemsim,'Toby'))
print('*******************')

#使用MovieLens数据集
def loadMovieLens(path='./data/movielens'):
    #获取影片标题
    movies={}
    for line in open(path+'/u.item'):
        (id,title)=line.split('|')[0:2]
        movies[id]=title
    #加载数据
    prefs={}
    for line in open(path+'/u.data'):
        (user,movieid,rating,ts)=line.split('\t')
        prefs.setdefault(user,{})
        prefs[user][movies[movieid]]=float(rating)
    return prefs

prefs=loadMovieLens()
print('加载数据->查看任意一位用户的评分情况:')
import random
user=prefs.keys()[random.randint(0,len(prefs)-1)]
print('用户:'+user)
print(prefs[user])
print('获取基于用户的推荐:')
print(getRecommendations(prefs,user)[0:30])
print('获取基于物品的推荐:')
itemsim=calculateSimilarItems(prefs,n=50)
print(getRecommendedItems(prefs,itemsim,user)[0:30])
print('***************')
    