import pytest

from unittest.mock import patch, AsyncMock

from clipper import Client


@pytest.mark.parametrize(
        "test_input",
        [
            ('url', ''),
            ('', 'token'),
            ('', ''),
        ]
)
def test_client_init__empty_inputs__session_none(test_input):
    client = Client(*test_input)

    assert client._session is None


@pytest.mark.asyncio
async def test_client_clip__session_none__empty_dict():
    client = Client(url='', token='')
    clip = await client.clip('url')

    assert clip == {}


@pytest.mark.asyncio
async def test_client_clip__session__dict():
    mocked_session = AsyncMock(name='mocked_session')
    mocked_response = AsyncMock(name='mocked_response')
    mocked_session.post.return_value = mocked_response

    with patch('clipper.aiohttp') as mocked_aiohttp:
        mocked_aiohttp.ClientSession.return_value = mocked_session

        client = Client(url='http://url.com/clipper', token='tokem')
        await client.clip('url')

        assert mocked_session.post.called
        assert mocked_response.json.called


@pytest.mark.asyncio
async def test_client_close__session__close():
    mocked_session = AsyncMock(name='mocked_session')

    with patch('clipper.aiohttp') as mocked_aiohttp:
        mocked_aiohttp.ClientSession.return_value = mocked_session

        client = Client(url='http://url.com/clipper', token='tokem')
        await client.close()

        assert mocked_session.close.called
