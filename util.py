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
      i = soup.find('div', class_='info_tv')

      # logger.debug(i.prettify())

      title = i.select_one('.txt_subject').text.strip()
      genre = i.find('dt', string=re.compile(u'^(장르|정보)$')).find_next_sibling('dd').text.split(',')[0].split('|')[0].strip()
      year = '' # TODO
      bb = i.find('dt', string="방영시간 정보").find_next_sibling('dd').select('.txt_info')

      logger.debug(bb[0].text.strip())
      logger.debug(bb[1].text.strip())
      logger.debug(bb[2].text.strip())

      info = {'title': title, 'genre': genre, 'year': year}
    except:
      logger.debug('parsing error:')
      logger.error(sys.exc_info())

  return info

def send_message(id, msg):
  t_bot.sendMessage(chat_id=id, text=msg)

if __name__ == '__main__':
  logger = log.setup_custom_logger()
  info = get_program_info(sys.argv[1].decode('utf-8'))
  logger.debug(info)
