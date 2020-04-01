import os
import time
import subprocess
import yaml
import telegram
from argparse import ArgumentParser
from celery import Celery


def get_app(**configs):
    token = configs["services"]["common"]["telegram"]["token"]
    chat_id = configs["services"]["common"]["telegram"]["chat_id"]

    broker = configs["services"]["common"]["celery"]["broker"] + "/nesta_notice"

    app = Celery("notice", broker=broker)
    
    @app.task(name="notice")
    def notice(msg):
        assert isinstance(msg, str)
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=chat_id, text=msg)

    return app
