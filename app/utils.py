import re

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
        raise ValueError(f'Invalid ttl value: {ttl}')

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

    try:
        calc = seconds_calc[unit]
    except KeyError as e:
        raise ValueError(f'Invalid unit argument value: {unit}')

    return calc(number)


def cache_key(key: str) -> str:
    return f'cache:{key}'


def clip_cache_key(key: str) -> str:
    return f'clip:{key}'


def clip_task_name(uid: str) -> str:
    return f'clip_{uid}'