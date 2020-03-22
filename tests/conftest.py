import pytest
from absinthe.server.server import Server
from absinthe.configs.util import parse_env, parse_config

@pytest.fixture(scope="session")
def server(request):
    yield