import pytest

import handlers
import constants as const
import utils

from unittest.mock import patch

from exceptions import InvalidParameters


@pytest.mark.asyncio
async def test_redirect__mocked_cache__value(mocked_cache, url, uid):
    mocked_cache.get.return_value = url

    result = await handlers.redirect(uid, mocked_cache)

    assert result == url
    mocked_cache.get.assert_called_with(utils.url_cache_key(uid))


@pytest.mark.asyncio
async def test_clip__mocked_cache__value(mocked_cache, url, uid):
    expected = (url, {'test_key', 'test_value'})
    mocked_cache.multi_get.return_value = expected

    with patch('handlers.clip_task_name') as mocked_clip_task_name:
        result = await handlers.clip(uid, mocked_cache)

        assert result == expected
        mocked_clip_task_name.assert_called()
        mocked_cache.multi_get.assert_called_with(utils.url_cache_key(uid), utils.clip_cache_key(uid))  # noqa


@pytest.mark.parametrize(
        "test_input",
        [
            {'url': 'test_url', 'ttl': '42s', 'clip': 'T', 'uid': 'test_uid'},
            {'url': 'test_url'},
        ]
)
def test_shortify_input__valid_input__valid_output(test_input):
    result = handlers._ShortifyInput(test_input)

    assert result.url and isinstance(result.url, str)
    assert result.ttl and isinstance(result.ttl, int)
    assert result.uid and isinstance(result.uid, str)
    assert isinstance(result.clip, bool)


def test_shortify_input__default_uid_len__uid():
    result = handlers._ShortifyInput({'url': 'test_url'})

    assert result.uid
    assert len(result.uid) == const.DEFAULT_UID_LEN


@pytest.mark.parametrize(
        "test_input",
        [
            {},
            {'url': ''},
            {'url': 'test_url', 'ttl': '12'},
            {'url': 'test_url', 'clip': 'False'},
            {'url': 'test_url', 'uid': 'health'},  # from const.KEY_WORDS
            {'url': 'test_url', 'uid': 'static'},  # from const.KEY_WORDS
        ]
)
def test_shortify_input__invalid_inputes__exception(test_input):
    with pytest.raises(InvalidParameters):
        handlers._ShortifyInput(test_input)


@pytest.mark.asyncio
async def test_clipper_task__moked_cache_clipper__clipped_cached(
        mocked_cache,
        mocked_clipper,
        url,
        uid,
        ttl,
        clip
):
    mocked_clipper.clip.return_value = clip

    await handlers._clipper_task(uid, url, ttl, mocked_cache, mocked_clipper)

    mocked_clipper.clip.assert_called_with(url)
    mocked_cache.set.assert_called_with(utils.clip_cache_key(uid), clip, ttl=ttl)  # noqa


@pytest.mark.asyncio
async def test_shortify__without_clip__uid(mocked_cache, mocked_clipper, url, uid, ttl_str, ttl):
    test_args = {'url': url, 'clip': 'false', 'uid': uid, 'ttl': ttl_str}

    result = await handlers.shortify(test_args, mocked_cache, mocked_clipper)

    assert result
    mocked_cache.set.assert_called_with(utils.url_cache_key(uid), url, ttl=ttl)
    mocked_clipper.clip.assert_not_called()


@pytest.mark.asyncio
async def test_shortify__with_clip__uid(mocked_cache, mocked_clipper, url, uid, ttl_str, ttl):
    test_args = {'url': url, 'clip': 'true', 'uid': uid, 'ttl': ttl_str}

    with patch('handlers.asyncio.Task') as mocked_task:
        result = await handlers.shortify(test_args, mocked_cache, mocked_clipper)

        assert result
        mocked_cache.set.assert_called_with(utils.url_cache_key(uid), url, ttl=ttl)
        mocked_task.assert_called()


@pytest.mark.asyncio
async def test_delete__mocked_cache__bool(mocked_cache, uid):
    mocked_cache.multi_delete.return_value = 2

    result = await handlers.delete(uid, mocked_cache)

    assert result
    mocked_cache.multi_delete.assert_called_with(utils.url_cache_key(uid), utils.clip_cache_key(uid))  # noqa
