from enum import Enum

LNK = 'lnk'

DEFAULT_TTL = 12 * 60 * 60  # seconds

INF = 'inf'

class TimeUnit(Enum):
    DAYS = 'days'
    HOURS = 'hours'
    MINUTES = 'minutes'
    SECONDS = 'seconds'
