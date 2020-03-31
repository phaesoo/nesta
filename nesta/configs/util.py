import os
import boto3
import yaml

def parse_env():
    # from environment variables
    env_list = [
        "ROOT_PATH",
        "MODE",
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
    bucket = "nesta-config"
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket, Key="debug.yml")
    return yaml.safe_load(response["Body"])


def get_defined_path(path, config):
    return path.format(**config)