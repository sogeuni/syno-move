# -*- coding: utf-8 -*-
import logging

LOGGER_NAME='synomove'
LOGGER_FILE_NAME='synomove.log'

def setup_custom_logger():
  formatter = logging.Formatter(fmt='%(asctime)s::%(levelname)s::%(module)s - %(message)s')

  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)

  file_handler = logging.FileHandler(LOGGER_FILE_NAME)
  file_handler.setFormatter(formatter)

  logger = logging.getLogger(LOGGER_NAME)
  logger.setLevel(logging.INFO)
  logger.addHandler(stream_handler)
  logger.addHandler(file_handler)
  return logger

def get_logger():
  return logging.getLogger(LOGGER_NAME)