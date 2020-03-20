import os
import yaml


def parse_config(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(filename)

    configs = dict()

    # from environment variables
    configs["ROOT_DIR"] = os.environ["ROOT_DIR"]

    # read from yaml
    configs.update(yaml.load(open(filename), Loader=yaml.Loader))
    
    return configs


def get_defined_path(path, config):
    return path.format(**config)