# -*- coding: utf-8 -*-
import signal
import sys
import time
from threading import Thread, Timer

import yaml
from persistqueue import Queue

import log
from util import Config

task_queue = Queue('move_task_queue')
n = 1

def move_file():
  while True:
    print('Consumer waiting')

    logger.info('aaa')

    t = task_queue.get()

    if t:
      print('Consumer working: ' + t)
      time.sleep(1)
      task_queue.task_done()

def scan_finished_files():
  global n
  print('put: ' + str(n))
  task_queue.put(str(n))
  n += 1
  
  Timer(0.3, scan_finished_files).start()

if __name__ == '__main__':
  logger = log.setup_custom_logger()

  logger.info('start SYNOMOVE')

  stream = open('config.yaml', 'r')
  config = Config(yaml.load(stream))

  logger.debug("config.host -> " + str(config.host))
  logger.debug("config.auth -> " + str(config.auth))

  move_thread = Thread(target=move_file)
  move_thread.daemon = True
  move_thread.start()

  scan_thread = Timer(1, scan_finished_files)
  scan_thread.daemon = True
  scan_thread.start()

  try: 
    while 1: 
      time.sleep(.1) 
  except KeyboardInterrupt: 
    logger.info("exit SYNOMOVE")
    sys.exit(0)
