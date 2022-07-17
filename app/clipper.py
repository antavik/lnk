import asyncio
import logging
import typing as t

import aiohttp

from urllib.parse import urlparse

log = logging.getLogger(__name__)


class Client:

    def __init__(
            self,
            url: str,
            token: str,
            timeout: int = 5,
            retry_timeout: int = 10
    ):
        self.url = urlparse(url)
        self.base_url = self.url.geturl().removesuffix(self.url.path)
        self.token = token
        self.timeout = aiohttp.ClientTimeout(total=timeout)

        self._session = aiohttp.ClientSession(
            base_url=self.base_url,
            headers={'x-user-id': self.token},
            timeout=self.timeout,
            raise_for_status=True,
        )

    async def clip(self, url: str) -> t.Optional[dict[str, str]]:
        try:
            response = await self._session.post(
                self.url.path, json={'url': url}
            )
        except Exception as e:
            log.error('error clipping: %s', e)
            return

        log.debug('url %s clipped', url)

        return await response.json()

    async def close(self):
        await self._session.close()
