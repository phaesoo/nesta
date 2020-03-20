import os
import sys
import logging
from logging import handlers



def init_logger(filepath, name):
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
    filename = os.path.join(filepath, f"{name}.log")
    log_handler = handlers.TimedRotatingFileHandler(filename=filename, when='midnight', interval=1, encoding='utf-8')
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