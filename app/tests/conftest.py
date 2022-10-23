import pytest
import random

from unittest.mock import AsyncMock

random.seed(42)


@pytest.fixture
def mocked_storage():
    return AsyncMock(name='mocked_storage')


@pytest.fixture
def mocked_clipper():
    return AsyncMock(name='mocked_clipper')


@pytest.fixture
def url():
    return 'test_url'


@pytest.fixture
def uid():
    return 'test_uid'


@pytest.fixture
def ttl_str():
    return '1s'


@pytest.fixture
def ttl():
    return 1


@pytest.fixture
def clip():
    return {'test_content': 'test'}
