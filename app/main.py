#!/usr/local/bin/python

import logging
import asyncio

import uvloop
import jinja2 as j2

import handlers
import clipper
import constants as const
import settings

from aiohttp import web

from storage import Redis, GzipJsonSerializer
from middlewares import compression_middleware
from exceptions import InvalidParameters, StillProcessing

log = logging.getLogger(const.LNK)

rendering_env = j2.Environment(
    loader=j2.FileSystemLoader(settings.TEMPLATE_PATH),
    autoescape=True,
    enable_async=True
)
redirect_template = rendering_env.get_template(
    settings.REDIRECT_TEMPLATE_FILENAME
)
empty_content_template = rendering_env.get_template(
    settings.EMPTY_TEMPLATE_FILENAME, parent=settings.BASE_TEMPLATE_FILENAME
)
text_content_template = rendering_env.get_template(
    settings.TEXT_CONTENT_TEMPLATE_FILENAME, parent=settings.BASE_TEMPLATE_FILENAME  # noqa
)
html_content_template = rendering_env.get_template(
    settings.HTML_CONTENT_TEMPLATE_FILENAME, parent=settings.BASE_TEMPLATE_FILENAME  # noqa
)  # noqa

routes = web.RouteTableDef()
routes.static('/static', settings.STATIC_PATH)


@routes.get('/health/ping')
async def view(request: web.Request) -> web.Response:
    return web.Response(text='pong')


@routes.get('/{uid}')
async def redirect(request: web.Request) -> web.Response:
    uid = request.match_info['uid']
    storage = request.app['storage']

    url = await handlers.redirect(uid, storage)
    if url is None:
        return web.Response(status=404, text='UID not found')

    html = await redirect_template.render_async(url=url)

    return web.Response(
        status=301,
        headers={
            'Location': url,
            'Cache-Control': 'private, max-age=60',
        },
        content_type='text/html',
        charset='utf-8',
        body=html
    )


@routes.get('/{uid}/text')
async def text_content(request: web.Request) -> web.Response:
    uid = request.match_info['uid']
    storage = request.app['storage']

    try:
        url, data = await handlers.clip(uid, storage)
    except StillProcessing:
        return web.Response(status=202, text='Clip in process')

    if url is None:
        return web.Response(status=404, text='Clip not found')

    if data:
        html = await text_content_template.render_async(url=url, **data)
    else:
        html = await empty_content_template.render_async(url=url)

    return web.Response(
        status=200,
        headers={
            'Cache-Control': 'private, max-age=60',
        },
        content_type='text/html',
        charset='utf-8',
        body=html
    )


@routes.get('/{uid}/html')
async def html_content(request: web.Request) -> web.Response:
    uid = request.match_info['uid']
    storage = request.app['storage']

    try:
        url, data = await handlers.clip(uid, storage)
    except StillProcessing:
        return web.Response(status=202, text='Clip in process')

    if url is None:
        return web.Response(status=404, text='Clip not found')

    if data:
        html = await html_content_template.render_async(url=url, **data)
    else:
        html = await empty_content_template.render_async(url=url)

    return web.Response(
        status=200,
        headers={
            'Cache-Control': 'private, max-age=60',
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
    storage = request.app['storage']
    clipper = request.app['clipper']

    try:
        uid = await handlers.shortify(form, storage, clipper)
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
    storage = request.app['storage']

    deleted = await handlers.delete(uid, storage)

    if deleted:
        return web.Response(status=200, text=f'UID {uid} removed')

    return web.Response(status=404, text=f'UID {uid} not found')


async def init_storage(app: web.Application):
    storage = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT if settings.REDIS_PORT is None else int(settings.REDIS_PORT),  # noqa
        serializer=GzipJsonSerializer()
    )
    if not await storage.ping():
        raise ConnectionError('cannot ping storage')

    app['storage'] = storage

    log.debug('storage initialized')


async def init_clipper(app: web.Application):
    app['clipper'] = clipper.Client(
        url=settings.CLIPPER_URL,
        token=settings.CLIPPER_TOKEN
    )

    log.debug('clipper initialized')


async def close_storage(app: web.Application):
    await app['storage'].close()


async def close_clipper(app: web.Application):
    if clipper := app['clipper']:
        await clipper.close()


def init_app():
    app = web.Application()
    app.middlewares.append(compression_middleware)
    app.add_routes(routes)

    app.on_startup.append(init_storage)
    app.on_startup.append(init_clipper)

    app.on_cleanup.append(close_storage)
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
