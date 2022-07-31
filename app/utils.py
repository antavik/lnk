import re
import typing as t

from constants import TimeUnit as TU


def parse_ttl(ttl: str) -> tuple[int, TU]:
    number = None
    units = None
    pattern = (
        f'^(?P<number>\d+)'
        f'((?P<{TU.DAYS.value}>d)|'
        f'(?P<{TU.HOURS.value}>h)|'
        f'(?P<{TU.MINUTES.value}>m)|'
        f'(?P<{TU.SECONDS.value}>s))'
    )

    match = re.fullmatch(pattern, ttl)
    if match is None:
        raise ValueError(f'invalid ttl value: {ttl}')

    groups = match.groupdict()
    number = groups.pop('number')

    for units, match in groups.items():
        if match is not None:
            break

    return (int(number), TU(units))


def calc_seconds(number: int, unit: TU) -> int:
    seconds_calc = {
        TU.DAYS: lambda d: d * 24 * 60 * 60,
        TU.HOURS: lambda h: h * 60 * 60,
        TU.MINUTES: lambda m: m * 60,
        TU.SECONDS: lambda s: s,
    }

    calc = seconds_calc.get(unit)
    if calc is None:
        raise ValueError(f'invalid unit argument value: {unit}')

    return calc(number)


def cache_key(key: str) -> str:
    return f'cache:{key}'


def clip_cache_key(key: str) -> str:
    return f'clip:{key}'


def clip_task_name(uid: str) -> str:
    return f'clip_{uid}'


def str2bool(value: str) -> bool:
    if not isinstance(value, str):
        raise TypeError('unsupported type')

    true_bool_strings = {'yes', 'y', '1', 'true', 't'}
    false_bool_strings = {'no', 'n', '0', 'false', 'f', ''}

    string_lower = str(value).lower()

    if string_lower in true_bool_strings:
        return True
    elif string_lower in false_bool_strings:
        return False
    else:
        raise ValueError('unsupported string value')
