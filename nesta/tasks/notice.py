import os
import time
import subprocess
import yaml
import telegram
from argparse import ArgumentParser
from celery import Celery


def get_notice(**configs):
    token = configs["services"]["common"]["telegram"]["token"]
    chat_id = configs["services"]["common"]["telegram"]["chat_id"]

    broker = configs["services"]["common"]["celery"]["broker"] + "/nesta_notice"

    app = Celery("notice", broker=broker)

    @app.task(name="info")
    def info(msg):
        assert isinstance(msg, str)
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=chat_id, text="[INFO] "+msg)

    @app.task(name="error")
    def error(msg):
        assert isinstance(msg, str)
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=chat_id, text="[ERROR] "+msg)

    @app.task(name="critical")
    def critical(msg):
        assert isinstance(msg, str)
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=chat_id, text="[CRITICAL] "+msg)

    return app
