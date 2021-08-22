import re

from typing import Literal

from constants import TimeUnit as TU

TimeUnit = Literal[
    TU.DAYS.value, TU.DAYS.value, TU.MINUTES.value, TU.SECONDS.value
]


def parse_ttl(ttl: str) -> tuple[int, TimeUnit]:
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
        raise Exception(f'Invalid ttl option {ttl}')

    groups = match.groupdict()
    number = groups.pop('number')

    for units, match in groups.items():
        if match is not None:
            break

    return int(number), units


def calc_seconds(number: int, unit: TimeUnit) -> int:
    seconds_calc = {
        TU.DAYS.value: lambda d: d * 24 * 60 * 60,
        TU.HOURS.value: lambda h: h * 60 * 60,
        TU.MINUTES.value: lambda m: m * 60,
        TU.SECONDS.value: lambda s: s,
    }

    calc = seconds_calc[unit]

    return calc(number)
