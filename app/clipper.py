import asyncio
import logging
import typing as t

import aiohttp
import ujson

import constants as const

from abc import ABC, abstractmethod
from urllib.parse import urlparse

log = logging.getLogger(const.LNK)


class BaseClipper(ABC):

    @abstractmethod
    async def clip(self, url: str) -> dict[str, str]:
        pass

    @abstractmethod
    async def close(self):
        pass


class Client(BaseClipper):

    def __init__(self, url: str, token: str, timeout: int = 10):
        self.url = urlparse(url)
        self.base_url = self.url.geturl().removesuffix(self.url.path)
        self.token = token
        self.timeout = timeout

        self._timeout = aiohttp.ClientTimeout(total=self.timeout)
        self._retries = 3
        self._retries_timeout = 1

        self._session: t.Optional[aiohttp.ClientSession] = None
        if self.base_url and self.token:
            self._session = aiohttp.ClientSession(
                base_url=self.base_url,
                headers={'x-user-id': self.token},
                timeout=self._timeout,
                raise_for_status=True,
                json_serialize=ujson.dumps,
            )

    async def clip(self, url: str) -> dict[str, str]:
        if self._session is None:
            return {}

        for retry in range(1, self._retries+1):
            try:
                response = await self._session.post(
                    self.url.path, json={'url': url, 'timeout': self.timeout}
                )
            except Exception as e:
                log.warning(
                    'error clipping: %s', str(e) or 'empty error message'
                )

                if retry < self._retries:
                    await asyncio.sleep(self._retries_timeout)
            else:
                log.debug('url clipped')

                return await response.json(loads=ujson.loads)

        return {}

    async def close(self):
        if self._session is not None:
            await self._session.close()

        log.debug('closed')


class Fake(BaseClipper):

    async def clip(self, url: str) -> dict[str, str]:
        return {'test_content': 'test'}

    async def close(self):
        pass
