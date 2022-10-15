import logging
import uuid
import asyncio

import ujson

import constants as const
import settings
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


async def clip(uid: str, cache: BaseCache) -> tuple[str | None, dict[str, str] | None]:  # noqa
    if clip_task_name(uid) in {f.get_name() for f in asyncio.all_tasks()}: 
        raise StillProcessing()

    return await cache.multi_get(url_cache_key(uid), clip_cache_key(uid))


async def shortify(data: dict, cache: BaseCache, clipper: clipper.Client) -> str:
    url = data.get('url')
    if not url:
        raise InvalidParameters('url not provided')

    ttl_str = data.get('ttl', const.DEFAULT_TTL)
    if ttl_str == const.INF_TTL:
        ttl = None
    else:
        try:
            number, unit = parse_ttl(ttl_str)
        except Exception as e:
            raise InvalidParameters(e)
        else:
            ttl = calc_seconds(number, unit)

    try:
        clip = str2bool(data.get('clip', 'true'))
    except Exception:
        raise InvalidParameters('invalid clip value')

    uid = data.get('uid', uuid.uuid4().hex[:settings.DEFAULT_UID_LEN])
    if uid in const.KEY_WORDS:
        raise InvalidParameters(f'"{uid}" couldn\'t be uid')

    await cache.set(url_cache_key(uid), url, ttl=ttl)

    if clip:
        asyncio.Task(
            _clipper_task(uid, url, ttl, cache, clipper),
            name=clip_task_name(uid)
        )

    return uid


async def _clipper_task(
        uid: str,
        url: str,
        ttl: int,
        cache: BaseCache,
        clipper: clipper.Client
):
    clip = await clipper.clip(url)
    await cache.set(clip_cache_key(uid), clip, ttl=ttl)


async def delete(uid: str, cache: BaseCache) -> bool:
    return await cache.multi_delete(url_cache_key(uid), clip_cache_key(uid))
