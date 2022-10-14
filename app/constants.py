from enum import Enum

LNK = 'lnk'

DEFAULT_TTL = '12h'
INF_TTL = 'inf'

class TimeUnit(Enum):
    DAYS = 'days'
    HOURS = 'hours'
    MINUTES = 'minutes'
    SECONDS = 'seconds'


KEY_WORDS = {'health', 'static',}
