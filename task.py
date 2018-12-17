# -*- coding: utf-8 -*-
import os
import re

import log

TV_SUFFIX=ur'(\s\d{1,2}-\d{1,2}회\s합본)?\.E\d{1,3}(\.END)?\.\d{6}\.(720|1080)p-NEXT(.mp4)?'

class Task():
  def __init__(self, dict):
    self.logger = log.get_logger()

    self.id = dict.get('id')
    self.file_name = dict.get('title')
    
    self.download_type = dict.get('type')
    self.download_status = dict.get('status')

    self.org = dict.get('additional').get('detail').get('destination')

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
        self.title = ''
        self.logger.error("not found suffix: " + self.file_name)
    except (TypeError, AttributeError) as e:
      self.logger.error(e)
      self.type = 'unknown'
      self.title = ''

    self.dest = os.path.join(self.title, self.file_name)
    
    self.debug_print()

  def is_complete(self):
    return (self.download_type == 'bt' and (self.download_status == 'seeding' or self.download_status == 'finished'))

  def debug_print(self):
    self.logger.debug('=============')
    self.logger.debug("id: " + self.id)
    self.logger.debug("file_name: " + self.file_name)
    self.logger.debug("title: " + self.title)
    self.logger.debug("type: " + self.type)
    self.logger.debug("download_type: " + self.download_type)
    self.logger.debug("download_status: " + self.download_status)
    self.logger.debug("org: " + self.org)
    self.logger.debug("dest: " + self.dest)
