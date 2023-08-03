import re

from enum import Enum

LNK = 'lnk'

KEY_WORDS = {'health', 'static', 'ping', 'lnk'}

DEFAULT_TTL = '12h'
INF_TTL = 'inf'

DEFAULT_UID_LEN = 6


class TimeUnit(Enum):
    DAYS = 'days'
    HOURS = 'hours'
    MINUTES = 'minutes'
    SECONDS = 'seconds'


SECONDS_CALC_MAP = {
    TimeUnit.DAYS: lambda d: d * 24 * 60 * 60,
    TimeUnit.HOURS: lambda h: h * 60 * 60,
    TimeUnit.MINUTES: lambda m: m * 60,
    TimeUnit.SECONDS: lambda s: s,
}


TTL_REGEXP = re.compile(
    f'^(?P<number>\\d+)'
    f'((?P<{TimeUnit.DAYS.value}>d)|'
    f'(?P<{TimeUnit.HOURS.value}>h)|'
    f'(?P<{TimeUnit.MINUTES.value}>m)|'
    f'(?P<{TimeUnit.SECONDS.value}>s))'
)
