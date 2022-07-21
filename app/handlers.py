import logging
import uuid
import typing as t
import asyncio

import ujson

import constants as const
import clipper

from aiocache import Cache

from utils import (
    parse_ttl,
    calc_seconds,
    cache_key,
    clip_cache_key,
    clip_task_name,
    str2bool,
)
from exceptions import InvalidParameters, StillProcessing


async def redirect(uid: str, cache: Cache) -> t.Optional[str]:
    return await cache.get(cache_key(uid))


async def clip(uid: str, cache: Cache) -> tuple[t.Optional[str], t.Optional[dict[str, str]]]:  # noqa
    if clip_task_name(uid) in {f.get_name() for f in asyncio.all_tasks()}: 
        raise StillProcessing()

    return await cache.multi_get((cache_key(uid), clip_cache_key(uid)))


async def shortify(data: dict, cache: Cache, clipper: clipper.Client) -> str:
    url = data.get('url')
    if not url:
        raise InvalidParameters('url not provided')

    ttl_str = data.get('ttl')
    if ttl_str is None:
        ttl = const.DEFAULT_TTL
    elif ttl_str == const.INF:
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

    uid = data.get('uid', uuid.uuid4().hex)

    await cache.add(cache_key(uid), url, ttl=ttl)

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
        cache: Cache,
        clipper: clipper.Client
):
    if clip := await clipper.clip(url):
        await cache.add(clip_cache_key(uid), clip, ttl=ttl)


async def delete(uid: str, cache: Cache) -> bool:
    deleted = 0
    for key in (cache_key(uid), clip_cache_key(uid)):
        deleted += await cache.delete(key)

    return bool(deleted)
