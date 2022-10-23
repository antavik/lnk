import pytest

import handlers
import constants as const
import utils

from unittest.mock import patch

from exceptions import InvalidParameters


@pytest.mark.asyncio
async def test_redirect__mocked_storage_value(mocked_storage, url, uid):
    mocked_storage.get.return_value = url

    result = await handlers.redirect(uid, mocked_storage)

    assert result == url
    mocked_storage.get.assert_called_with(utils.url_storage_key(uid))


@pytest.mark.asyncio
async def test_clip__mocked_storage__value(mocked_storage, url, uid):
    expected = (url, {'test_key', 'test_value'})
    mocked_storage.multi_get.return_value = expected

    with patch('handlers.clip_task_name') as mocked_clip_task_name:
        result = await handlers.clip(uid, mocked_storage)

        assert result == expected
        mocked_clip_task_name.assert_called()
        mocked_storage.multi_get.assert_called_with(utils.url_storage_key(uid), utils.clip_storage_key(uid))  # noqa


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
async def test_clipper_task__moked_storage_clipper__clipped_storaged(
        mocked_storage,
        mocked_clipper,
        url,
        uid,
        ttl,
        clip
):
    mocked_clipper.clip.return_value = clip

    await handlers._clipper_task(uid, url, ttl, mocked_storage, mocked_clipper)

    mocked_clipper.clip.assert_called_with(url)
    mocked_storage.set.assert_called_with(utils.clip_storage_key(uid), clip, ttl=ttl)  # noqa


@pytest.mark.asyncio
async def test_shortify__without_clip__uid(
        mocked_storage,
        mocked_clipper,
        url,
        uid,
        ttl_str,
        ttl
):
    test_args = {'url': url, 'clip': 'false', 'uid': uid, 'ttl': ttl_str}

    result = await handlers.shortify(test_args, mocked_storage, mocked_clipper)

    assert result
    mocked_storage.set.assert_called_with(utils.url_storage_key(uid), url, ttl=ttl)  # noqa
    mocked_clipper.clip.assert_not_called()


@pytest.mark.asyncio
async def test_delete__mocked_storage__bool(mocked_storage, uid):
    mocked_storage.multi_delete.return_value = 2

    result = await handlers.delete(uid, mocked_storage)

    assert result
    mocked_storage.multi_delete.assert_called_with(utils.url_storage_key(uid), utils.clip_storage_key(uid))  # noqa
