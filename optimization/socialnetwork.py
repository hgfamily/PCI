#-*- coding:utf-8 -*-
#网络可视化
import math
import optimization


people=['Charlie','Augustus','Veruca','Violet','Mike','Joe','Willy','Miranda']

links=[('Augustus', 'Willy'), 
       ('Mike', 'Joe'), 
       ('Miranda', 'Mike'), 
       ('Violet', 'Augustus'), 
       ('Miranda', 'Willy'), 
       ('Charlie', 'Mike'), 
       ('Veruca', 'Joe'), 
       ('Miranda', 'Augustus'), 
       ('Willy', 'Augustus'), 
       ('Joe', 'Charlie'), 
       ('Veruca', 'Augustus'), 
       ('Miranda', 'Joe')]
#计算交叉线
def crosscount(v):
    # 将数字序列转换成一个person:(x,y)字典
    loc=dict([(people[i],(v[i*2],v[i*2+1])) for i in range(0,len(people))])
    total=0

    # 遍历每一对连线
    for i in range(len(links)):
        for j in range(i+1,len(links)):

            # 获取坐标位置 
            (x1,y1),(x2,y2)=loc[links[i][0]],loc[links[i][1]]
            (x3,y3),(x4,y4)=loc[links[j][0]],loc[links[j][1]]

            den=(float)((y4-y3)*(x2-x1)-(x4-x3)*(y2-y1))

            # 如果两线平行 则den==0 
            if den==0: continue

            # 否则ua与ub就是两条交叉线的分数值
            ua=(float)((x4-x3)*(y1-y3)-(y4-y3)*(x1-x3))/den
            ub=(float)((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3))/den

            # 如果两条线的分数值介于0和1之间，则两线彼此交叉
            if ua>0 and ua<1 and ub>0 and ub<1:
                total+=1
        for i in range(len(people)):
            for j in range(i+1,len(people)):
                # 获得两结点的位置
                (x1,y1),(x2,y2)=loc[people[i]],loc[people[j]]

                # 计算两结点间的距离
                dist=math.sqrt(math.pow(x1-x2,2)+math.pow(y1-y2,2))
                # 对间距小于50个像素的结点进行判罚
                if dist<50:
                    total+=(1.0-(dist/50.0))

    return total
#测试网络可视化
"""
domain=[(10,370)]*(len(people)*2)
sol=optimization.randomoptimize(domain,crosscount)
print crosscount(sol)
"""
from PIL import Image,ImageDraw
#绘制网络
def drawnetwork(sol,jpeg='socialnetwork.jpeg'):
    # 建立image对象
    img=Image.new('RGB',(400,400),(255,255,255))
    draw=ImageDraw.Draw(img)

    # 建立标示位置信息的字典
    pos=dict([(people[i],(sol[i*2],sol[i*2+1])) for i in range(0,len(people))])

    #绘制连线
    for (a,b) in links:
        draw.line((pos[a],pos[b]),fill=(255,0,0))
    #绘制代表人的结点
    for n,p in pos.items():
        draw.text(p,n,(0,0,0))

    img.save(jpeg,'jpeg')

#测试绘制网络
domain=[(10,370)]*(len(people)*2)
#sol=optimization.annealingoptimize(domain,crosscount,step=50,cool=0.99)
sol=optimization.randomoptimize(domain,crosscount)
drawnetwork(sol)