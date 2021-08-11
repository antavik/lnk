import os
import logging
import asyncio

import constants as const
import handlers

from urllib.parse import urljoin

from aiohttp import web
from aiocache import Cache

from exceptions import InvalidParemeters

HOST, PORT = os.environ['HOST'], os.environ['PORT']
CACHE = os.getenv('CACHE', 'memory://')

with open(const.UI_TEMPLATE_FILEPATH) as template:
    UI_TEMPLATE = template.read()

routes = web.RouteTableDef()


@routes.get('/health/ping')
async def view(request):
    return web.Response(content_type='text/plain', text='pong')


@routes.get('/{uid}')
async def redirect(request):
    uid = request.match_info['uid']
    cache = request.app['cache']

    url = await handlers.redirect(uid, cache)

    if url is not None:
        return web.HTTPFound(url)

    raise web.HTTPNotFound()


@routes.post('/')
async def shortify(request):
    if not request.can_read_body:
        return web.HTTPBadRequest(
            content_type='text/plain',
            text='Empty body'
        )

    cache = request.app['cache']
    data = await request.json()

    try:
        uid = await handlers.shortify(data, cache)
    except InvalidParemeters as e:
        return web.HTTPBadRequest(
            content_type='text/plain',
            text=str(e)
        )
    except ValueError:
        return web.HTTPConflict(
            content_type='text/plain',
            text='UID already exists'
        )

    return web.Response(
        content_type='text/plain',
        text=uid
    )


async def init_cache(app):
    cache = Cache.from_url(CACHE)

    app['cache'] = cache


async def close_cache(app):
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
