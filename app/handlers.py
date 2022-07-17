import logging
import uuid
import typing as t

import constants as const
import clipper

from aiocache import Cache

from utils import parse_ttl, calc_seconds, cache_key
from exceptions import InvalidParameters


async def redirect(uid: str, cache: Cache) -> t.Optional[str]:
    return await cache.get(cache_key(uid))


async def clip(
        uid: str,
        cache: Cache,
        clipper: clipper.Client
) -> tuple[t.Optional[str], t.Optional[dict[str, str]]]:
    url = await cache.get(cache_key(uid))
    if url is None:
        return (None, None)

    data = await clipper.clip(url)

    return (url, data)

async def shortify(data: dict, cache: Cache) -> str:
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

    await cache.add(cache_key(uid), url, ttl=ttl)

    return uid


async def delete(uid: str, cache: Cache) -> bool:
    deleted = await cache.delete(cache_key(uid))

    return bool(deleted)
