import logging
import uuid

import constants as const

from utils import parse_ttl, calc_seconds
from exceptions import InvalidParemeters


async def redirect(uid, cache):
    key = f'cache:{uid}'
    url = await cache.get(key)

    return url

async def shortify(data, cache):
    try:
        url = data['url']
    except KeyError as e:
        logging.error(e)
        raise InvalidParemeters('No URL parameter')

    uid = data.get('uid', uuid.uuid1().hex)

    ttl_str = data.get('ttl')
    if ttl_str is None:
        ttl = const.DEFAULT_TTL
    else:
        try:
            number, unit = parse_ttl(ttl_str)
        except Exception as e:
            logging.error(e)
            raise InvalidParemeters('Invalid input TTL praremeter')
        else:
            ttl = calc_seconds(number, unit)

    key = f'cache:{uid}'

    await cache.add(key, url, ttl=ttl)

    return uid
