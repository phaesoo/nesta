import os
import yaml

def parse_env():
    # from environment variables
    env_list = [
        "ROOT_PATH",
        "CONFIG_PATH",
        ]

    env_dict = {}
    undefined = []
    for key in env_list:
        val = os.environ.get(f"NESTA_{key}")
        if val is None:
            undefined.append(f"NESTA_{key}")
            continue
        env_dict[key] = val

    if len(undefined):
        raise ValueError(f"Environment variable has not been exported: {undefined}")

    return env_dict

def parse_config(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(filename)
    # read from yaml
    return yaml.load(open(filename), Loader=yaml.Loader)


def get_defined_path(path, config):
    return path.format(**config)