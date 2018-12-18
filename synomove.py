# -*- coding: utf-8 -*-
import os
import signal
import subprocess
import sys
import time
from threading import Thread, Timer
from urlparse import urlparse

import persistqueue
import yaml

import log
from synopy.api import DownloadStationTask
from synopy.base import Connection
from task import Task
from util import Config

TEST = False

file_dir = os.path.dirname(os.path.abspath(__file__))
move_task_queue = persistqueue.Queue(os.path.join(file_dir, 'move_task_queue'))

def move_file():
  while True:
    logger.info('wait move_file')
    item = move_task_queue.get()

    if item:
      task = Task(config, item)
      cmd = config.command 
        + '"' + os.path.join(config.org_root, task.org_path).encode('utf-8') + '"'
        + '"' + os.path.join(config.dest_root, task.dest_path).encode('utf-8') + '"'
      logger.info("move start:" + cmd)
      
      if not TEST:
        try:
          ret = subprocess.call(cmd, shell=True)
        except (subprocess.CalledProcessError, TypeError, OSError) as e:
          ret = 1000
          logger.error(e)
        finally:
          if ret == 0:
            logger.info('move success: ' + task.file_name)
          else:
            logger.error('move error: ' + task.file_name)
            move_task_queue.put(item)

      move_task_queue.task_done()
      time.sleep(1)

def scan_torrent():
  logger.info('scan_torrent')
  dstask_api = DownloadStationTask(conn, version=1)
  # Use the 'list' query method to see the running tasks
  resp = dstask_api.list(additional='detail,file')

  logger.debug(resp.payload)

  if resp.is_success():
    items = resp.payload.get('data').get('tasks')

    for item in items:
      task = Task(config, item)
      task.debug_print()

      if task.is_complete():
        logger.info('delete torrent: ' + task.file_name)

        if not TEST:
          result = dstask_api.delete(id=task.id)
          logger.debug(result.payload)
          if result.payload.get('success'):
            logger.info('put in queue: ' + task.file_name)
            move_task_queue.put(item)
        else:
          logger.info('put in queue: ' + task.file_name)
          move_task_queue.put(item)
        
  Timer(config.scan_interval, scan_torrent).start()

if __name__ == '__main__':
  logger = log.setup_custom_logger()
  logger.info('start SYNOMOVE')

  # TODO: config path 설정
  
  config_path = os.path.join(file_dir, 'config.yaml')
  logger.info('load config file: ' + config_path)
  stream = open(config_path, 'r')
  config = Config(yaml.load(stream))

  logger.info('Connect to ' + config.server)
  url = urlparse(config.server)

  # connect to DSM
  conn = Connection(url.scheme, url.hostname, port=url.port)
  conn.authenticate(config.account, config.passwd)

  move_thread = Thread(target=move_file)
  move_thread.daemon = True
  move_thread.start()

  scan_thread = Timer(0, scan_torrent)
  scan_thread.daemon = True
  scan_thread.start()

  # ctrl+c로 종료
  try: 
    while 1: 
      time.sleep(.1) 
  except KeyboardInterrupt: 
    logger.info("exit SYNOMOVE")
    sys.exit(0)
