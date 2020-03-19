import os
import yaml


def parse_config(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(filename)

    # read from yaml
    configs = yaml.load(open(filename), Loader=yaml.Loader)

    # from environment variables
    configs["ROOT_DIR"] = os.environ["ROOT_DIR"]
    
    return configs