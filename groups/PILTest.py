# -*- coding:utf-8 -*-
from PIL import Image, ImageDraw, ImageFilter, ImageFont
#test PIL
"""
im = Image.new('RGB', (300,300), 'white')
draw = ImageDraw.Draw(im)
font = ImageFont.truetype('arial.ttf', 14)
draw.text((100,100), 'test text', font = font)
"""
#test BeautifulSoup4
from bs4 import BeautifulSoup
from urllib import urlopen
"""
soup=BeautifulSoup(urlopen('http://www.lfd.uci.edu'),'lxml')
print(soup.head.title)
link=soup('a')
"""
html = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title" name="dromouse"><b>The Dormouse's story</b></p>
<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1"><!-- Elsie --></a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>
<p class="story">...</p>
"""
soup=BeautifulSoup(html,'lxml')
#格式化内容输出
print(soup.prettify())
print('-------------')
c=soup.contents
for t in c:print(t)
print('-----------')
#获取tag
print(soup.title)
print(soup.head)
print(soup.a)
print(soup.p)
print(type(soup.a))
print(soup.name)
print(soup.head.name)
print(soup.p.attrs)
print(soup.p['class'])
print('-----------')
#获取NavigableString
print(soup.p.string)
print(type(soup.p.string))
print(soup.name)
print(soup.attrs)