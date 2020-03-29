import os
import sys
import logging
import logstash
from logging import handlers



def init_logger(filepath, name, log_level):
    print (log_level)
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
    filename = os.path.join(filepath, f"{name}.log")
    log_handler = handlers.TimedRotatingFileHandler(filename=filename, when='midnight', interval=1, encoding='utf-8')
    log_handler.setFormatter(formatter)
    log_handler.suffix = "%Y%m%d"

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)
    stream_handler.suffix = "%Y%m%d"

    ##logstash_handler.setFormatter(formatter)
    #logstash_handler.suffix = "%Y%m%d"

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.addHandler(log_handler)
    # logger.addHandler(stream_handler)
    logger.addHandler(logstash.TCPLogstashHandler("localhost", 5000, version=1))

    return logger