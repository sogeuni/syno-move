# -*- coding: utf-8 -*-
import os
import re

import requests
from bs4 import BeautifulSoup

import log

TV_SUFFIX=ur'(\s\d{1,2}-\d{1,2}회\s합본)?\.E\d{1,4}(\.END)?\.\d{6}\.(720|1080)p-NEXT(.mp4)?'
QUERY=u'https://search.daum.net/search?w=tv&q='
program_infos = {}

class Task():
  def __init__(self, config, dict):
    self.logger = log.get_logger()

    self.id = dict.get('id')
    self.file_name = dict.get('title')
    
    self.download_type = dict.get('type')
    self.download_status = dict.get('status')

    self._org_path = os.path.join(dict.get('additional').get('detail').get('destination'), self.file_name)
    self.type = 'unknown'
    self.title = ''
    self.ext_title = ''
    self.ext_year = ''
    self.ext_genre = ''

    self._parse_info()
    if len(self.title) > 0:
      self._get_additional_info()

  def _parse_info(self):
    p = re.compile(TV_SUFFIX)

    try:
      # file_name에서 TV_SUFFIX와 일치하는 문자열 찾음
      m = p.search(self.file_name)

      if m:
        self.type = 'tv'
        self.title = p.sub('', self.file_name)
      else:
        # suffix가 일치하지 않는 경우 movie로 판단
        # TODO: movie 처리
        self.type = 'movie'
        self.logger.error("not found suffix: " + self.file_name)
    except (TypeError, AttributeError) as e:
      self.logger.error(e)

  def _get_additional_info(self):
    info = program_infos.get(self.title)

    if info:
      self.logger.info('found from cache')
      self.ext_title = info.get('title')
      self.ext_year = info.get('year')
      self.ext_genre = info.get('genre')
    else:
      self.logger.info('get info from web')
      req = requests.get(QUERY + self.title)
      soup = BeautifulSoup(req.text, "html.parser")
      info = soup.find('div', class_='info_cont')

      self.logger.debug(info.prettify())

      # 페이지 구조에 따라 변경될 수 있음
      self.ext_title = info.find('div', class_='tit_program').text.strip() # programe title
      self.ext_year = info.select_one('span:nth-of-type(3)').text.strip().split('.')[0]
      self.ext_genre = info.find('dd', class_='cont').text.strip() # genre

      # programe 정보를 캐싱
      program_infos[self.title] = { 'title': self.ext_title, 'year': self.ext_year, 'genre': self.ext_genre }

  def is_complete(self):
    return (self.download_type == 'bt'
      and self.type == 'tv'
      and (self.download_status == 'seeding' or self.download_status == 'finished'))

  @property
  def org_path(self):
    return self._org_path
  
  @property
  def dest_path(self):
    if len(self.ext_title) > 0:
      program_title = self.ext_title
    else:
      program_title = self.title
    
    return os.path.join(self.ext_genre, self.ext_year, program_title, self.file_name)

  def debug_print(self):
    self.logger.debug('=============')
    self.logger.debug("id: " + self.id)
    self.logger.debug("file_name: " + self.file_name)
    self.logger.debug("title: " + self.title)
    self.logger.debug("type: " + self.type)
    self.logger.debug("ext_title: " + self.ext_title)
    self.logger.debug('ext_year: ' + self.ext_year)
    self.logger.debug('ext_genre: ' + self.ext_genre)
    self.logger.debug("download_type: " + self.download_type)
    self.logger.debug("download_status: " + self.download_status)
    self.logger.debug('============')
