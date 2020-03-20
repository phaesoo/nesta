import pytest

@pytest.fixture(scope="sessions")
def server():
    yield
