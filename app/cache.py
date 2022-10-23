import typing as t
import gzip

import ujson
import redis.asyncio as aioredis

from abc import ABC, abstractmethod


class BaseSerializer(ABC):

    @abstractmethod
    def dumps(self, obj: t.Any) -> bytes | None:
        pass

    @abstractmethod
    def loads(self, data: bytes | None) -> t.Any:
        pass


class GzipJsonSerializer(BaseSerializer):

    DEFAULT_COMPRESSLEVEL = 8

    def dumps(self, obj: t.Any) -> bytes | None:
        if obj is None:
            return None

        return gzip.compress(
            ujson.dumps(obj).encode('utf-8'),
            compresslevel=self.DEFAULT_COMPRESSLEVEL
        )

    def loads(self, data: bytes | None) -> t.Any:
        if data is None:
            return None

        return ujson.loads(gzip.decompress(data))


class BaseCache(ABC):

    @abstractmethod
    async def get(self, key: t.Any) -> t.Any:
        pass

    @abstractmethod
    async def multi_get(self, *keys: t.Any) -> t.Iterable[t.Any]:
        pass

    @abstractmethod
    async def set(
            self,
            key: t.Any,
            value: t.Any,
            ttl: t.Optional[int | float] = None
    ):
        pass

    @abstractmethod
    async def multi_delete(self, *keys: t.Any) -> int:
        pass

    @abstractmethod
    async def ping(self) -> bool:
        pass


class Redis(BaseCache):

    def __init__(
            self,
            host: str,
            port: t.Optional[int] = None,
            decode_responses: bool = False,
            health_check_interval: int = 0,
            serializer: t.Optional[BaseSerializer] = None,
            _client: t.Callable = aioredis.Redis
    ):
        self.host = host
        self.port = port or 6379
        self.serializer = serializer
        self.decode_responses = decode_responses
        self.health_check_interval = health_check_interval
        self.serializer = serializer

        self._client = _client(
            host=self.host,
            port=self.port,
            decode_responses=self.decode_responses,
            health_check_interval=self.health_check_interval
        )

    async def get(self, key: t.Any) -> t.Any:
        value = await self._client.get(key)

        if self.serializer is not None:
            return self.serializer.loads(value)

        return value

    async def multi_get(self, *keys: t.Any) -> t.Iterable[t.Any]:
        values = await self._client.mget(*keys)

        if self.serializer is not None:
            return [self.serializer.loads(v) for v in values]

        return values

    async def set(
            self,
            key: t.Any,
            value: t.Any,
            ttl: t.Optional[int | float] = None
    ):
        if self.serializer is not None:
            value = self.serializer.dumps(value)

        await self._client.set(key, value, ex=ttl)

    async def multi_delete(self, *keys: t.Any) -> int:
        return await self._client.delete(*keys)

    async def ping(self) -> bool:
        return await self._client.ping()


class Fake(BaseCache):

    def __init__(self):
        self._storage = {}

    async def get(self, key: t.Any) -> t.Any:
        return self._storage.get(key)

    async def multi_get(self, *keys: t.Any) -> t.Iterable[t.Any]:
        return [self._storage.get(k) for k in keys]

    async def set(
            self,
            key: t.Any,
            value: t.Any,
            ttl: t.Optional[int | float] = None
    ):
        self._storage[key] = value

    async def multi_delete(self, *keys: t.Any) -> int:
        deleted = 0

        for k in keys:
            try:
                del self._storage[k]
            except KeyError:
                continue
            else:
                deleted += 1

        return deleted

    async def ping(self) -> bool:
        return True
