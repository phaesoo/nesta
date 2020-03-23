import pytest
from absinthe.control.control import Control
from absinthe.configs.util import parse_env, parse_config

@pytest.fixture(scope="session")
def control():
    env_dict = parse_env()
    configs = parse_config(env_dict["CONFIG_PATH"])
    ctrl = Control(configs=configs)
    yield ctrl
