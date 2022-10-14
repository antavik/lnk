#!/usr/local/bin/python

import os
import logging
import asyncio
import gzip
import typing as t

import uvloop
import jinja2 as j2

import handlers
import clipper
import constants as const
import settings

from pathlib import Path

from aiohttp import web
from aiocache import Cache
from aiocache.serializers import JsonSerializer

from middlewares import compression_middleware
from exceptions import InvalidParameters, StillProcessing

log = logging.getLogger(const.LNK)

rendering_env = j2.Environment(
    loader=j2.FileSystemLoader(settings.TEMPLATE_PATH),
    autoescape=True,
    enable_async=True
)
redirect_template = rendering_env.get_template(settings.REDIRECT_TEMPLATE_FILENAME)
empty_content_template = rendering_env.get_template(
    settings.EMPTY_TEMPLATE_FILENAME, parent=settings.BASE_TEMPLATE_FILENAME
)
text_content_template = rendering_env.get_template(
    settings.TEXT_CONTENT_TEMPLATE_FILENAME, parent=settings.BASE_TEMPLATE_FILENAME
)  # noqa
html_content_template = rendering_env.get_template(
    settings.HTML_CONTENT_TEMPLATE_FILENAME, parent=settings.BASE_TEMPLATE_FILENAME
)  # noqa

routes = web.RouteTableDef()
routes.static('/static', settings.STATIC_PATH)


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

    html = await redirect_template.render_async(url=url)

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


@routes.get('/{uid}/text')
async def text_content(request: web.Request) -> web.Response:
    uid = request.match_info['uid']
    cache = request.app['cache']

    try:
        url, data = await handlers.clip(uid, cache)
    except StillProcessing:
        return web.Response(status=202, text='Clip in process')

    if url is None:
        return web.Response(status=404, text='Clip not found')

    template = text_content_template if data else empty_content_template
    html = await template.render_async(url=url, **data)

    return web.Response(
        status=200,
        headers={
            'Cache-Control':'private, max-age=60',
        },
        content_type='text/html',
        charset='utf-8',
        body=html
    )


@routes.get('/{uid}/html')
async def html_content(request: web.Request) -> web.Response:
    uid = request.match_info['uid']
    cache = request.app['cache']

    try:
        url, data = await handlers.clip(uid, cache)
    except StillProcessing:
        return web.Response(status=202, text='Clip in process')

    if url is None:
        return web.Response(status=404, text='Clip not found')

    template = html_content_template if data else empty_content_template
    html = await template.render_async(url=url, **data)

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
    if request.headers.get('X-Lnk-Token') != settings.TOKEN:
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
    except ValueError:
        return web.Response(status=409, text='UID already exists')

    return web.Response(status=201, text=uid)


@routes.delete('/{uid}')
async def delete(request: web.Request) -> web.Response:
    if request.headers.get('X-Lnk-Token') != settings.TOKEN:
        return web.Response(status=403)

    uid = request.match_info['uid']
    cache = request.app['cache']

    deleted = await handlers.delete(uid, cache)

    if deleted:
        return web.Response(status=200, text=f'UID {uid} removed')

    return web.Response(status=404, text=f'UID {uid} not found')


async def init_cache(app: web.Application):

    class GzipJsonSerializer(JsonSerializer):

        DEFAULT_COMPTESSLEVEL = 8

        def dumps(self, value: t.Any) -> bytes:
            return gzip.compress(
                super().dumps(value).encode('utf-8'),
                compresslevel=self.DEFAULT_COMPTESSLEVEL
            )

        def loads(self, value: bytes) -> t.Any:
            return super().loads(gzip.decompress(value).decode())

    cache = Cache.from_url(settings.CACHE)
    cache.serializer=GzipJsonSerializer()

    app['cache'] = cache

    log.debug('cache initialized')


async def init_clipper(app: web.Application):
    app['clipper'] = clipper.Client(
        url=settings.CLIPPER_URL,
        token=settings.CLIPPER_TOKEN
    )

    log.debug('clipper initialized')


async def close_cache(app: web.Application):
    await app['cache'].close()


async def close_clipper(app: web.Application):
    if clipper := app['clipper']:
        await clipper.close()


def init_app():
    app = web.Application()
    app.middlewares.append(compression_middleware)
    app.add_routes(routes)

    app.on_startup.append(init_cache)
    app.on_startup.append(init_clipper)

    app.on_cleanup.append(close_cache)
    app.on_cleanup.append(close_clipper)

    return app


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format=settings.LOG_FORMAT,
        datefmt=settings.LOG_DATEFMT
    )

    web.run_app(init_app(), host=settings.HOST, port=settings.PORT)


if __name__ == '__main__':
    import sys

    if sys.version_info >= (3, 11):  # TODO: check code below after upgrade to 3.11  # noqa
        with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
            runner.run(main())
    else:
        uvloop.install()

        main()
