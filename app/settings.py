import os
import logging

from pathlib import Path

TOKEN = os.environ['TOKEN']
if not TOKEN:
    raise EnvironmentError('token should be valid string')

HOST, PORT = os.getenv('HOST', '0.0.0.0'), os.getenv('PORT', '8010')

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT')

CLIPPER_URL, CLIPPER_TOKEN = os.getenv('CLIPPER_URL', ''), os.getenv('CLIPPER_TOKEN', '')  # noqa

CWD = Path.cwd()
TEMPLATE_PATH = CWD / 'templates'
REDIRECT_TEMPLATE_FILENAME = 'redirect.html'
BASE_TEMPLATE_FILENAME = 'base.html'
EMPTY_TEMPLATE_FILENAME = 'empty.html'
TEXT_CONTENT_TEMPLATE_FILENAME = 'text.html'
HTML_CONTENT_TEMPLATE_FILENAME = 'html.html'
STATIC_PATH = CWD / 'static'

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(message)s'
LOG_DATEFMT = '%Y-%m-%dT%H:%M:%S'

DEFAULT_UID_LEN = 12

os.environ.clear()