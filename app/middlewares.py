from typing import Any, Callable, Coroutine

from aiohttp import hdrs
from aiohttp.web import (
    middleware,
    Request,
    StreamResponse,
    Response,
    ContentCoding,
)

HandlerType = Callable[[Any], Coroutine[Any, None, Response]]


# idea from https://github.com/mosquito/aiohttp-compress
@middleware
async def compression_middleware(
        request: Request,
        handler: HandlerType
) -> StreamResponse:
    accept_encoding = request.headers.get(hdrs.ACCEPT_ENCODING, '').lower()

    if ContentCoding.gzip.value in accept_encoding:
        compressor = ContentCoding.gzip.value
    elif ContentCoding.deflate.value in accept_encoding:
        compressor = ContentCoding.deflate.value
    else:
        return await handler(request)

    response = await handler(request)
    response.headers[hdrs.CONTENT_ENCODING] = compressor
    response.enable_compression()

    return response
