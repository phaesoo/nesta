import os
from celery.bin import worker
from argparse import ArgumentParser
from nesta.tasks.tasks import get_worker
from nesta.tasks.notice import get_notice
from nesta.configs.util import parse_env, parse_config
from nesta.external.daemon import Daemon
from celery.bin.celeryd_detach import detached_celeryd


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("--name", dest="name", type=str,
                        help="worker name(worker, notice)", required=True)
    return parser.parse_args()


class Worker(Daemon):
    def __init__(self, name, configs):
        assert isinstance(configs, dict)
        conf = configs["services"].get(name)
        if conf is None:
            raise ValueError(
                "Config does not defined for service: {}".format(name))

        logfile = conf["logfile"]
        super().__init__(
            pidfile=conf["pidfile"],
            stdout=logfile,
            stderr=logfile
        )

        app = None
        if name == "worker":
            app = get_worker(**configs)
        elif name == "notice":
            app = get_notice(**configs)
        else:
            raise ValueError("Unknown worker name: {}".format(name))
        self._worker = worker.worker(app=app)
        
        self._config = {
            "logfile": conf["logfile"],
            "loglevel": conf["loglevel"],
            "traceback": True,
        }

    def _run(self):
        self._worker.run(**self._config)


if __name__ == "__main__":
    env_dict = parse_env()
    configs = parse_config(env_dict["MODE"])

    options = parse_arguments()

    w = Worker(options.name, configs=configs)
    w.start()