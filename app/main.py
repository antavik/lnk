#!/usr/local/bin/python

import os
import logging
import asyncio

import handlers

from aiohttp import web
from aiocache import Cache

from exceptions import InvalidParameters

TOKEN = os.environ['TOKEN']
if not TOKEN:
    raise Exception('Token should be valid string')

HOST, PORT = os.getenv('HOST', '0.0.0.0'), os.getenv('PORT', '8010')
CACHE = os.getenv('CACHE', 'memory://')

os.environ.clear()

routes = web.RouteTableDef()


@routes.get('/health/ping')
async def view(request: web.Request) -> web.Response:
    return web.Response(text='pong')


@routes.get('/{uid}')
async def redirect(request: web.Request) -> web.Response:
    uid = request.match_info['uid']
    cache = request.app['cache']

    url = await handlers.redirect(uid, cache)

    if url is not None:
        return web.Response(
            status=301,
            headers={
                'Location': url,
                'Cache-Control':'private, max-age=60',
            }
        )

    return web.Response(status=404, text='UID not found')


@routes.post('/')
async def shortify(request: web.Request) -> web.Response:
    if request.headers.get('X-Lnk-Token') != TOKEN:
        return web.Response(status=403)

    if not request.can_read_body:
        return web.Response(status=400, text='Empty body')

    data = await request.post()
    cache = request.app['cache']

    try:
        uid = await handlers.shortify(data, cache)
    except InvalidParameters as e:
        return web.Response(status=400, text=f'Invalid input parameter: {e}')
    except ValueError as e:
        return web.Response(status=409, text='UID already exists')

    return web.Response(status=201, text=uid)


@routes.delete('/{uid}')
async def delete(request: web.Request) -> web.Response:
    if request.headers.get('X-Lnk-Token') != TOKEN:
        return web.Response(status=403)

    uid = request.match_info['uid']
    cache = request.app['cache']

    deleted = await handlers.delete(uid, cache)

    if deleted:
        return web.Response(status=204, text=f'UID {uid} removed')

    return web.Response(status=404, text=f'UID {uid} not found')


async def init_cache(app: web.Application):
    cache = Cache.from_url(CACHE)

    app['cache'] = cache


async def close_cache(app: web.Application):
    await app['cache'].close()


async def init_app():
    app = web.Application()
    app.add_routes(routes)

    app.on_startup.append(init_cache)
    app.on_cleanup.append(close_cache)

    return app


def main():
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())

    web.run_app(app, host=HOST, port=PORT)


if __name__ == '__main__':
    main()
