import os
import time
import subprocess
import yaml
import telegram
from argparse import ArgumentParser
from celery import Celery


def get_notice(**configs):
    assert isinstance(configs, dict)

    token = configs["services"]["common"]["telegram"]["token"]
    chat_id = configs["services"]["common"]["telegram"]["chat_id"]

    broker = configs["services"]["common"]["celery"]["broker"] + "/nesta_notice"

    app = Celery("notice", broker=broker)

    @app.task(name="notice")
    def notice(level, msg):
        if level not in ["INFO", "ERROR", "CRITICAL"]:
            raise ValueError("Undefined level: {}".format(level))
        assert isinstance(msg, str)
        assert len(msg)
        assert isinstance(msg, str)
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=chat_id, text="[{}] {}".format(level, msg))

    return app
