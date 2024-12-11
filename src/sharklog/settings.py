import logging

DEFAULT_LEVEL = logging.INFO
DEFAULT_FORMAT = "[%(levelname)s]: %(message)s [%(asctime)s](%(filename)s:%(lineno)d)"

SHARKLOG_FORMATTER = logging.Formatter(
    fmt=DEFAULT_FORMAT,
)

SHARKLOG_STREAM_HANDLER = logging.StreamHandler()
SHARKLOG_STREAM_HANDLER.setFormatter(SHARKLOG_FORMATTER)
