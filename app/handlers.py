import uuid
import asyncio

import constants as const
import clipper

from cache import BaseCache
from utils import (
    parse_ttl,
    calc_seconds,
    url_cache_key,
    clip_cache_key,
    clip_task_name,
    str2bool,
)
from exceptions import InvalidParameters, StillProcessing


async def redirect(uid: str, cache: BaseCache) -> str | None:
    return await cache.get(url_cache_key(uid))


async def clip(
        uid: str,
        cache: BaseCache
) -> tuple[str | None, dict[str, str] | None]:
    if clip_task_name(uid) in {f.get_name() for f in asyncio.all_tasks()}:
        raise StillProcessing()

    return await cache.multi_get(url_cache_key(uid), clip_cache_key(uid))


async def shortify(
        data: dict,
        cache: BaseCache,
        clipper: clipper.BaseClipper
) -> str:
    input_args = _ShortifyInput(data)

    await cache.set(
        url_cache_key(input_args.uid), input_args.url, ttl=input_args.ttl
    )

    if input_args.clip:
        asyncio.Task(
            _clipper_task(
                input_args.uid, input_args.url, input_args.ttl, cache, clipper
            ),
            name=clip_task_name(input_args.uid)
        )

    return input_args.uid


class _ShortifyInput:

    def __init__(self, data: dict[str, str]):
        self._data = data

        self.url = self._data.get('url', '')
        if not self.url:
            raise InvalidParameters('url not provided')

        self.ttl: int | None = None
        self.ttl_str = self._data.get('ttl', const.DEFAULT_TTL)
        if self.ttl_str != const.INF_TTL:
            try:
                number, unit = parse_ttl(self.ttl_str)
            except Exception as e:
                raise InvalidParameters(e)
            else:
                self.ttl = calc_seconds(number, unit)

        try:
            self.clip = str2bool(self._data.get('clip', 'true'))
        except Exception:
            raise InvalidParameters('invalid clip value')

        self.uid = self._data.get('uid', uuid.uuid4().hex[:const.DEFAULT_UID_LEN])  # noqa
        if self.uid in const.KEY_WORDS:
            raise InvalidParameters(f'"{self.uid}" couldn\'t be uid')


async def _clipper_task(
        uid: str,
        url: str,
        ttl: int | None,
        cache: BaseCache,
        clipper: clipper.BaseClipper
):
    clip = await clipper.clip(url)
    await cache.set(clip_cache_key(uid), clip, ttl=ttl)


async def delete(uid: str, cache: BaseCache) -> bool:
    deleted = await cache.multi_delete(url_cache_key(uid), clip_cache_key(uid))

    return bool(deleted)
