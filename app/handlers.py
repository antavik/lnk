import logging
import uuid
import typing as t

import ujson

import constants as const
import clipper

from aiocache import Cache

from utils import parse_ttl, calc_seconds, cache_key, clip_cache_key
from exceptions import InvalidParameters


async def redirect(uid: str, cache: Cache) -> t.Optional[str]:
    url = await cache.get(cache_key(uid))

    return url


async def clip(uid: str, cache: Cache) -> tuple[t.Optional[str], t.Optional[dict[str, str]]]:
    url, data = await cache.multi_get((cache_key(uid), clip_cache_key(uid)))

    return (url, data)


async def shortify(data: dict, cache: Cache, clipper: clipper.Client) -> str:
    url = data.get('url')
    if not url:
        raise InvalidParameters('Url not provided')

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

    uid = data.get('uid', uuid.uuid1().hex)
    clip = await clipper.clip(url)

    await cache.multi_set(
        (
            (cache_key(uid), url),
            (clip_cache_key(uid), clip.get('content')),
        ),
        ttl=ttl
    )

    return uid


async def delete(uid: str, cache: Cache) -> bool:
    deleted = 0
    for key in (cache_key(uid), clip_cache_key(uid)):
        deleted += await cache.delete(key)

    return bool(deleted)
