import asyncio
import logging
import typing as t

import aiohttp
import ujson

import constants as const

from urllib.parse import urlparse

log = logging.getLogger(const.LNK)


class Client:

    def __init__(self, url: str, token: str, timeout: int = 10):
        self.url = urlparse(url)
        self.base_url = self.url.geturl().removesuffix(self.url.path)
        self.token = token
        self.timeout = timeout

        self._timeout = aiohttp.ClientTimeout(total=self.timeout)
        self._retries = 3
        self._retries_timeout = 1

        if self.base_url and self.token:
            self._session = aiohttp.ClientSession(
                base_url=self.base_url,
                headers={'x-user-id': self.token},
                timeout=self._timeout,
                raise_for_status=True,
                json_serialize=ujson.dumps
            )
        else:
            self._session = None

    async def clip(self, url: str) -> dict[str, str]:
        if self._session is None:
            return {}

        for retry in range(self._retries):
            try:
                response = await self._session.post(
                    self.url.path, json={'url': url, 'timeout': self.timeout}
                )
            except Exception as e:
                log.error('error clipping: %s', str(e) or 'empty error message')

                if retry < (self._retries - 1):
                    await asyncio.sleep(self._retries_timeout)
            else:
                log.debug('url clipped')

                return await response.json()

        return {}

    async def close(self):
        if self._session is not None:
            await self._session.close()
