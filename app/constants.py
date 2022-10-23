from enum import Enum

LNK = 'lnk'

KEY_WORDS = {'health', 'static'}

DEFAULT_TTL = '12h'
INF_TTL = 'inf'

DEFAULT_UID_LEN = 10


class TimeUnit(Enum):
    DAYS = 'days'
    HOURS = 'hours'
    MINUTES = 'minutes'
    SECONDS = 'seconds'
