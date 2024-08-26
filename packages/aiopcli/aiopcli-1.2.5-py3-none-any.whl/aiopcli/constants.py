from typing import Literal

LogLevel = Literal['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
DEFAULT_LOG_LEVEL = 'WARNING'
REF_REGEX = '^[-._a-zA-Z][-._a-zA-Z0-9]*$'
HOST_REGEX = r'^https?://'
