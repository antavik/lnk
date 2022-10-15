import typing as t
import asyncio
import gzip

import ujson
import redis.asyncio as aioredis

from abc import ABC, abstractmethod


class BaseSerializer(ABC):

    @abstractmethod
    def dumps(self, obj: t.Any) -> bytes:
        pass

    @abstractmethod
    def loads(self, b: bytes) -> t.Any:
        pass


class GzipJsonSerializer(BaseSerializer):

    DEFAULT_COMPTESSLEVEL = 8

    def dumps(self, obj: t.Any) -> bytes|None:
        if obj is None:
            return None

        return gzip.compress(
            ujson.dumps(obj).encode('utf-8'),
            compresslevel=self.DEFAULT_COMPTESSLEVEL
        )

    def loads(self, b: bytes|None) -> t.Any:
        if b is None:
            return None

        return ujson.loads(gzip.decompress(b))


class BaseCache(ABC):

    def __init__(
            self,
            host: str,
            port: t.Optional[int] = None,
            decode_responses: bool = False,
            health_check_interval: int = 0,
            serializer: t.Optional[BaseSerializer] = None
    ):
        self.host = host
        self.port = port or 6379
        self.serializer = serializer
        self.decode_responses = decode_responses
        self.health_check_interval = health_check_interval
        self.serializer = serializer

    @abstractmethod
    async def get(self, key: str) -> t.Any:
        pass

    @abstractmethod
    async def multi_get(self, *keys) -> t.Iterable[t.Any]:
        pass

    @abstractmethod
    async def set(
            self,
            key: str,
            value: t.Any,
            ttl: t.Optional[int|float] = None
    ) -> t.Any:
        pass

    @abstractmethod
    async def multi_delete(self, *keys: tuple[str]) -> int:
        pass

    @abstractmethod
    async def ping(self, *keys: tuple[str]) -> int:
        pass


class Redis(BaseCache):

    def __init__(
            self,
            host: str,
            port: t.Optional[int] = None,
            decode_responses: bool = False,
            health_check_interval: int = 0,
            serializer: t.Optional[BaseSerializer] = None
    ):
        super().__init__(
            host, port, decode_responses, health_check_interval, serializer
        )

        self._client = aioredis.Redis(
            host=self.host,
            port=self.port,
            decode_responses=self.decode_responses,
            health_check_interval=self.health_check_interval
        )

    async def get(self, key: str) -> t.Any:
        value = await self._client.get(key)

        if self.serializer is not None:
            return self.serializer.loads(value)

        return value

    async def multi_get(self, *keys: tuple[str]) -> t.Iterable[t.Any]:
        values = await self._client.mget(*keys)

        if self.serializer is not None:
            return [self.serializer.loads(v) for v in values]

        return values

    async def set(self, key: str, value: t.Any, ttl: t.Optional[int|float] = None) -> t.Any:
        if self.serializer is not None:
            value = self.serializer.dumps(value)

        await self._client.set(key, value, ex=ttl)

    async def multi_delete(self, *keys) -> int:
        return await self._client.delete(*keys)

    async def ping(self) -> bool:
        return await self._client.ping()
