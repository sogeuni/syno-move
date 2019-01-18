# -*- coding: utf-8 -*-
import re
import sys

import requests
import telegram
import yaml
from bs4 import BeautifulSoup

import log

QUERY=u'https://m.search.daum.net/search?w=tv&q='
program_infos = {}

T_TOKEN='627101228:AAH7WRbfzkkq-Ra38cFftpBbvzmDqtjpPso'
t_bot = telegram.Bot(token = T_TOKEN)

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

    try:
      info_tv = soup.find('div', class_='info_tv')

      # logger.debug(info_tv.prettify())

      title = info_tv.select_one('.txt_subject').text.strip()
      i = info_tv.find('dt', string=re.compile(u'^정보$'))

      if i is not None:
        logger.info('case 1')
        i = i.find_next_sibling('dd').text.split('|')
        genre = i[0].strip()
        year = i[1].split('.')[0].strip()
        i = info_tv.find('dt', string="방영시간 정보").find_next_sibling('dd').select('.txt_info')
        channel = i[0].text.strip()
      else:
        logger.info('case 2')
        i = info_tv.find('dt', string=re.compile(u'^장르$'))
        genre = i.find_next_sibling('dd').text.split(',')[0].strip()
        i = info_tv.find('dt', string="방영시간 정보").find_next_sibling('dd').select('.txt_info')
        channel = i[0].text.strip()
        year = i[2].text.split('.')[0].strip()

      info = {'title': title, 'channel': channel, 'genre': genre, 'year': year}
    except:
      logger.debug('parsing error:')
      logger.error(sys.exc_info())

  return info

def send_message(id, msg):
  try:
    t_bot.sendMessage(chat_id=id, text=msg)
  except:
    logger = log.get_logger()
    logger.error(sys.exc_info())

if __name__ == '__main__':
  logger = log.setup_custom_logger()
  info = get_program_info(sys.argv[1].decode('utf-8'))
  logger.debug(info)
