# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

q = u'땐뽀걸즈'

req = requests.get(u'https://search.daum.net/search?w=tv&q='+q)
html = req.text
soup = BeautifulSoup(html, "html.parser")
info = soup.find('div', class_='info_cont')

print info.prettify()
print info.find('div', class_='tit_program').text.strip() # programe title
print info.find('dd', class_='cont').text.strip() # genre

# print info.select('.txt_summary')
# print str(info.find_all('dd')).encode('utf-8')