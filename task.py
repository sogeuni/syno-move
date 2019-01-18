# -*- coding: utf-8 -*-
import os
import re
import sys

import log
import util

TV_SUFFIX=ur'(?:\s(?P<e1>\d{1,4})-(?P<e2>\d{1,4})회\s합본)?\.E(?P<ep>\d{1,4})(?P<suf>(?:\.END)?\.\d{6}\.(?:720|1080)p-NEXT(?:.mp4)?)'

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

    self._parse_info()
    print(len(self.title))
    if len(self.title) > 0:
      self.logger.info('get external info:')
      self.ext_info = util.get_program_info(self.title)

  def _parse_info(self):
    p = re.compile(TV_SUFFIX)

    try:
      # file_name에서 TV_SUFFIX와 일치하는 문자열 찾음
      m = p.search(self.file_name)

      if m:
        self.type = 'tv'
        self.title = p.sub('', self.file_name)
        rename_list = []

        # 파일명에 '##-##회 합본'이 있을 경우 PLEX에서 지원하는 형태(E##E##)로 이름 변경
        if m.group('e1') and m.group('e2'):
          rename_list = [self.title, '.E', m.group('e1').zfill(2), 'E', m.group('e2').zfill(2), m.group('suf')]
        else:
          rename_list = [self.title, '.E', m.group('ep'), m.group('suf')]

        # 제목에 숫자가 들어간경우 PLEX에서 파싱이 제대로 되지 않을 수 있으므로 시즌정보('S01') 추가
        if util.has_number(self.title):
          rename_list[1] = '.S01E'

        self.rename_file_name = ''.join(rename_list)
        self.logger.info('rename: ' + self.file_name + ' -> ' + self.rename_file_name)
      else:
        # suffix가 일치하지 않는 경우 movie로 판단
        # TODO: movie 처리
        self.type = 'movie'
        self.logger.error("not found suffix: " + self.file_name)
    except (TypeError, AttributeError) as e:
      self.logger.error(e)

  def is_complete(self):
    return (self.download_type == 'bt'
      and self.type == 'tv'
      and (self.download_status == 'seeding' or self.download_status == 'finished'))

  @property
  def org_path(self):
    return self._org_path

  @property
  def dest_path(self):
    try:
      if len(self.ext_info['title']) > 0:
        program_title = self.ext_info['title']
      else:
        program_title = self.title

      # TODO: path 설정가능하도록 수정
      if self.rename_file_name:
        file_name = self.rename_file_name
      else:
        file_name = self.file_name

      return os.path.join(self.ext_info['genre'], program_title, file_name)
    except:
      self.logger.error(sys.exc_info())
      return os.path.join(self.title, self.file_name)

  def debug_print(self):
    self.logger.debug('=== ' + self.file_name)
    self.logger.debug("id: " + self.id)
    self.logger.debug("title: " + self.title)
    self.logger.debug("type: " + self.type)
    self.logger.debug("download_type: " + self.download_type)
    self.logger.debug("download_status: " + self.download_status)
    if hasattr(self, 'ext_info') and self.ext_info is not None:
      self.logger.debug("ext_title: " + self.ext_info['title'])
      self.logger.debug('ext_year: ' + self.ext_info['year'])
      self.logger.debug('ext_genre: ' + self.ext_info['genre'])
    self.logger.debug('======')
