import pytest


@pytest.fixture(scope='function')
def hello_pygit():
    return 'Hello PyGit!'
