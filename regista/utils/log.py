import os
import sys
import logging
from logging import handlers


__LOG_DIR = "./log"


def init_logger(name):
    if not os.path.exists(__LOG_DIR):
        os.makedirs(__LOG_DIR)

    formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
    log_handler = handlers.TimedRotatingFileHandler(filename=os.path.join(__LOG_DIR, "test.log"), when='midnight', interval=1, encoding='utf-8')
    log_handler.setFormatter(formatter)
    log_handler.suffix = "%Y%m%d"

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    stream_handler.suffix = "%Y%m%d"

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(log_handler)
    logger.addHandler(stream_handler)