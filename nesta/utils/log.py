import os
import sys
import logging
import logstash
from logging import handlers



def init_logger(name, logfile, loglevel):
    logpath = os.path.dirname(logfile)
    if not os.path.exists(logpath):
        os.makedirs(logpath)

    formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
    filename = os.path.join(logfile)
    file_handler = handlers.TimedRotatingFileHandler(filename=filename, when='midnight', interval=1, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.suffix = "%Y%m%d"

    logger = logging.getLogger(name)
    logger.setLevel(loglevel)
    logger.addHandler(file_handler)

    return logger