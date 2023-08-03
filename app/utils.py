import re

from constants import TimeUnit as TU, LNK


_TTL_REGEXP = re.compile(
    f'^(?P<number>\\d+)'
    f'((?P<{TU.DAYS.value}>d)|'
    f'(?P<{TU.HOURS.value}>h)|'
    f'(?P<{TU.MINUTES.value}>m)|'
    f'(?P<{TU.SECONDS.value}>s))'
)


def parse_ttl(ttl: str) -> tuple[int, TU]:
    number = None
    units = None

    match = _TTL_REGEXP.fullmatch(ttl)
    if match is None:
        raise ValueError(f'invalid ttl value: {ttl}')

    groups: dict = match.groupdict()
    number = groups.pop('number')

    for units, match in groups.items():
        if match is not None:
            break

    return (int(number), TU(units))


_SECONDS_CALC_MAP = {
    TU.DAYS: lambda d: d * 24 * 60 * 60,
    TU.HOURS: lambda h: h * 60 * 60,
    TU.MINUTES: lambda m: m * 60,
    TU.SECONDS: lambda s: s,
}


def calc_seconds(number: int, unit: TU) -> int:
    calc = _SECONDS_CALC_MAP.get(unit)
    if calc is None:
        raise ValueError(f'invalid unit argument value: {unit}')

    return calc(number)


def url_storage_key(key: str) -> str:
    return f'{LNK}-u:{key}'


def clip_storage_key(key: str) -> str:
    return f'{LNK}-c:{key}'


def clip_task_name(uid: str) -> str:
    return f'clip_{uid}'


_TRUE_BOOL_STRINGS = {'yes', 'YES', 'y', 'Y', '1', 'true', 'TRUE', 't', 'T'}
_FALSE_BOOL_STRINGS = {'no', 'NO', 'n', 'N', '0', 'false', 'FALSE', 'f', 'F', ''}  # noqa


def str2bool(value: str) -> bool:
    if isinstance(value, bool):
        return value

    if value in _TRUE_BOOL_STRINGS:
        return True
    elif value in _FALSE_BOOL_STRINGS:
        return False

    raise ValueError('unsupported value')
