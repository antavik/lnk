#!/usr/local/bin/python

import os
import logging
import asyncio

import jinja2 as j2

import handlers
import clipper
import constants as const

from pathlib import Path

from aiohttp import web
from aiocache import Cache
from aiocache.serializers import JsonSerializer

from exceptions import InvalidParameters

log = logging.getLogger(const.LNK)

TOKEN = os.environ['TOKEN']
if not TOKEN:
    raise Exception('Token should be valid string')

HOST, PORT = os.getenv('HOST', '0.0.0.0'), os.getenv('PORT', '8010')
CACHE = os.getenv('CACHE', 'memory://')
CLIPPER_URL, CLIPPER_TOKEN = os.getenv('CLIPPER_URL', ''), os.getenv('CLIPPER_TOKEN', '')  # noqa

os.environ.clear()

CWD = Path.cwd()
TEMPLATE_PATH = CWD / 'templates'
BASE_TEMPLATE_FILENAME = 'base.html'
CLIP_TEMPLATE_FILENAME = 'clip.html'

rendering_env = j2.Environment(
    loader=j2.FileSystemLoader(TEMPLATE_PATH),
    autoescape=True,
    enable_async=True
)
base_template = rendering_env.get_template(BASE_TEMPLATE_FILENAME)
clip_template = rendering_env.get_template(CLIP_TEMPLATE_FILENAME)

routes = web.RouteTableDef()


@routes.get('/health/ping')
async def view(request: web.Request) -> web.Response:
    return web.Response(text='pong')


@routes.get('/{uid}')
async def redirect(request: web.Request) -> web.Response:
    uid = request.match_info['uid']
    cache = request.app['cache']

    url = await handlers.redirect(uid, cache)
    if url is None:
        return web.Response(status=404, text='UID not found')

    html = await base_template.render_async(url=url)

    return web.Response(
        status=301,
        headers={
            'Location': url,
            'Cache-Control':'private, max-age=60',
        },
        content_type='text/html',
        charset='utf-8',
        body=html
    )


@routes.get('/{uid}/clip')
async def redirect(request: web.Request) -> web.Response:
    uid = request.match_info['uid']
    cache = request.app['cache']

    url, data = await handlers.clip(uid, cache)
    if url is None or data is None:
        return web.Response(status=404, text='Clip not found')

    html = await clip_template.render_async(url=url, data=data)

    return web.Response(
        status=200,
        headers={
            'Cache-Control':'private, max-age=60',
        },
        content_type='text/html',
        charset='utf-8',
        body=html
    )


@routes.post('/')
async def shortify(request: web.Request) -> web.Response:
    if request.headers.get('X-Lnk-Token') != TOKEN:
        return web.Response(status=403)

    if not request.can_read_body:
        return web.Response(status=400, text='Empty body')

    form = await request.post()
    cache = request.app['cache']
    clipper = request.app['clipper']

    try:
        uid = await handlers.shortify(form, cache, clipper)
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
        return web.Response(status=200, text=f'UID {uid} removed')

    return web.Response(status=404, text=f'UID {uid} not found')


async def init_cache(app: web.Application):
    cache = Cache.from_url(CACHE)
    cache.serializer=JsonSerializer()

    app['cache'] = cache

    log.debug('cache initialized')


async def init_clipper(app: web.Application):
    client = clipper.Client(url=CLIPPER_URL, token=CLIPPER_TOKEN)

    app['clipper'] = client

    log.debug('clipper initialized')


async def close_cache(app: web.Application):
    await app['cache'].close()


async def close_clipper(app: web.Application):
    if clipper := app['clipper']:
        await clipper.close()


async def init_app():
    app = web.Application()
    app.add_routes(routes)

    app.on_startup.append(init_cache)
    app.on_startup.append(init_clipper)

    app.on_cleanup.append(close_cache)
    app.on_cleanup.append(close_clipper)

    return app


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s:%(filename)s:%(lineno)d %(message)s',  # noqa
        datefmt='%Y-%m-%dT%H:%M:%S'
    )

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())

    web.run_app(app, host=HOST, port=PORT)


if __name__ == '__main__':
    main()
