import logging
import uuid

import constants as const

from aiocache import Cache

from utils import parse_ttl, calc_seconds, cache_key
from exceptions import InvalidParameters


async def redirect(uid: str, cache: Cache) -> str:
    url = await cache.get(cache_key(uid))

    return url


async def shortify(data: dict, cache: Cache) -> str:
    try:
        url = data['url']
    except KeyError as e:
        raise InvalidParameters('Url is not provided')

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
