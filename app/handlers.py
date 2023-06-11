import uuid
import asyncio

import shortuuid

import constants as const
import clipper

from storage import BaseStorage
from utils import (
    parse_ttl,
    calc_seconds,
    url_storage_key,
    clip_storage_key,
    clip_task_name,
    str2bool,
)
from exceptions import InvalidParameters, StillProcessing


async def redirect(uid: str, storage: BaseStorage) -> str | None:
    return await storage.get(url_storage_key(uid))


async def clip(
        uid: str,
        storage: BaseStorage
) -> tuple[str | None, dict[str, str] | None]:
    if clip_task_name(uid) in {f.get_name() for f in asyncio.all_tasks()}:
        raise StillProcessing()

    return await storage.multi_get(url_storage_key(uid), clip_storage_key(uid))


async def shortify(
        data: dict,
        storage: BaseStorage,
        clipper: clipper.BaseClipper
) -> str:
    input_args = _ShortifyInput(data)

    await storage.set(
        url_storage_key(input_args.uid), input_args.url, ttl=input_args.ttl
    )

    if input_args.clip:
        asyncio.Task(
            _clipper_task(
                input_args.uid, input_args.url, input_args.ttl, storage, clipper  # noqa
            ),
            name=clip_task_name(input_args.uid)
        )

    return input_args.uid


class _ShortifyInput:

    __slots__ = ('_data', 'url', 'ttl', 'ttl_str', 'clip', 'uid')

    def __init__(self, data: dict[str, str]):
        self._data = data

        self.url = self._data.get('url', '')
        if not self.url:
            raise InvalidParameters('url not provided')

        self.ttl: int | None = None
        self.ttl_str = self._data.get('ttl', const.DEFAULT_TTL)
        if self.ttl_str != const.INF_TTL:
            try:
                number, unit = parse_ttl(self.ttl_str)
            except Exception as e:
                raise InvalidParameters(e)
            else:
                self.ttl = calc_seconds(number, unit)

        try:
            self.clip = str2bool(self._data.get('clip', 'true'))
        except Exception:
            raise InvalidParameters('invalid clip value')

        self.uid = self._data.get('uid', shortuuid.random(length=const.DEFAULT_UID_LEN))  # noqa
        if self.uid in const.KEY_WORDS:
            raise InvalidParameters(f'"{self.uid}" couldn\'t be uid')


async def _clipper_task(
        uid: str,
        url: str,
        ttl: int | None,
        storage: BaseStorage,
        clipper: clipper.BaseClipper
):
    clip = await clipper.clip(url)
    await storage.set(clip_storage_key(uid), clip, ttl=ttl)


async def delete(uid: str, storage: BaseStorage) -> bool:
    deleted = await storage.multi_delete(url_storage_key(uid), clip_storage_key(uid))  # noqa

    return bool(deleted)
