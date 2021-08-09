from pathlib import Path
from enum import Enum

CWD = Path.cwd()
TEMPLATES_PATH = CWD / 'templates'
UI_TEMPLATE_FILENAME = 'index.html'
UI_TEMPLATE_FILEPATH = TEMPLATES_PATH / UI_TEMPLATE_FILENAME
STATIC_PATH = CWD / 'static'
DEFAULT_TTL = 12 * 60 * 60  # seconds


class TimeUnit(Enum):
    DAYS = 'days'
    HOURS = 'hours'
    MINUTES = 'minutes'
    SECONDS = 'seconds'
