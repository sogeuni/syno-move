# -*- coding: utf-8 -*-
import logging
import os

LOGGER_NAME='synomove'
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "synomove.log")

def setup_custom_logger():
  formatter = logging.Formatter(fmt='%(asctime)s::%(levelname)s::%(module)s - %(message)s')

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)

  file_handler = logging.FileHandler(LOG_FILE)
  file_handler.setFormatter(formatter)

  logger = logging.getLogger(LOGGER_NAME)
  logger.setLevel(logging.INFO)
  logger.addHandler(stream_handler)
  logger.addHandler(file_handler)
  return logger

def get_logger():
  return logging.getLogger(LOGGER_NAME)
