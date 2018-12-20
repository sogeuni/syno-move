# -*- coding: utf-8 -*-
import requests
import yaml
from bs4 import BeautifulSoup

import log
import re

QUERY=u'https://m.search.daum.net/search?w=tv&q='
program_infos = {}

class Config(dict):
  def __init__(self, *args, **kwargs):
    dict.__init__(self, *args, **kwargs)
    self.logger = log.get_logger()

  def __getattr__(self, name):
    try:
      value = self[name]
      if isinstance(value, dict):
        value = Config(value)
      return value
    except KeyError:
      self.logger.error('Config not found - k: ' + name)
      pass

def get_program_info(title):
  logger = log.get_logger()

  info = program_infos.get(title)

  if not info:
    logger.info('get info from web: ' + title)
    req = requests.get(QUERY + title)
    soup = BeautifulSoup(req.text, "html.parser")

    i = soup.find('div', class_='info_tv')

    logger.debug(i.prettify())
    print(i.prettify())

    try:
      title = i.select_one('.txt_subject').text.strip()
      genre = i.find('dt', string=re.compile(u'^(장르|정보)$')).find_next_sibling('dd').text.split(',')[0].split('|')[0].strip()
      bb = i.find('dt', string="방영시간 정보").find_next_sibling('dd').select('.txt_info')

      print(title)
      print(genre)
      print(bb[0].text)
      print(bb[1].text)
      print(bb[2].text)
    except:
      print('error')

    # # 페이지 구조에 따라 변경될 수 있음
    # title = info.find('div', class_='tit_program').text.strip() # programe title
    # year = info.select_one('span:nth-of-type(3)').text.strip().split('.')[0]
    # genre = info.find('dd', class_='cont').text.strip() # genre

    # # programe 정보를 캐싱
    # info = { 'title': title, 'year': year, 'genre': genre }
    # program_infos[title] = info
    
  # logger.debug(info)
  return info

if __name__ == '__main__':
  get_program_info(u'나의 아저씨')
  get_program_info(u'땐뽀걸즈')
