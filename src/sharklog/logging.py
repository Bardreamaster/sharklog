import inspect
import logging
import sys

# Re-export the standard library API so that ``from sharklog import logging``
# can replace ``import logging``. The helpers defined below (getLogger, debug,
# info, ...) intentionally shadow their standard library counterparts.
from logging import *  # noqa: F401,F403

from sharklog import settings, utils
from sharklog.formatter import ColoredFormatter, supports_color

__all__ = [*logging.__all__, "init", "reset_all"]


def init(name: str = None, debug: bool = False, level=None, **kwargs):
    if debug:
        kwargs["level"] = logging.DEBUG
    elif level is not None:
        kwargs["level"] = utils.parse_level(level)
    else:
        kwargs["level"] = settings.DEFAULT_LEVEL

    kwargs["format"] = kwargs.get("format", settings.DEFAULT_FORMAT)

    custom_format = kwargs.get("format")
    handler = logging.StreamHandler()
    formatter_class = (
        ColoredFormatter if supports_color(handler.stream) else logging.Formatter
    )
    formatter = formatter_class(
        fmt=custom_format,
        datefmt=kwargs.get("datefmt"),
        style=kwargs.get("style", "%"),
    )
    handler.setFormatter(formatter)
    if not name:
        name = utils.resolve_name(inspect.currentframe().f_back.f_globals)
    logger = logging.getLogger(name)
    _replace_sharklog_handler(logger, handler)
    logger.setLevel(kwargs["level"])
    return logger


def _replace_sharklog_handler(logger, handler):
    """Attach ``handler``, dropping any handler a previous init() added.

    Calling init() again (e.g. to change the level or format) must not stack
    handlers, otherwise every message is printed once per call.
    """
    for old_handler in list(logger.handlers):
        if getattr(old_handler, "_sharklog_handler", False):
            logger.removeHandler(old_handler)
    handler._sharklog_handler = True
    logger.addHandler(handler)


def reset_all(debug=False, level=None, **kwargs):
    if debug:
        settings.DEFAULT_LEVEL = logging.DEBUG
    elif level is not None:
        settings.DEFAULT_LEVEL = utils.parse_level(level)

    kwargs["level"] = kwargs.get("level", settings.DEFAULT_LEVEL)
    kwargs["format"] = kwargs.get("format", settings.DEFAULT_FORMAT)
    logging.basicConfig(**kwargs)

    # basicConfig() is a no-op once the root logger has handlers (e.g. on a
    # second reset_all() call), so apply the level and format explicitly.
    logging.root.setLevel(kwargs["level"])
    formatter = logging.Formatter(
        fmt=kwargs["format"],
        datefmt=kwargs.get("datefmt"),
        style=kwargs.get("style", "%"),
    )
    for handler in logging.root.handlers:
        handler.setFormatter(formatter)


def getLogger(name=None):
    if not name:
        name = utils.resolve_name(inspect.currentframe().f_back.f_globals)
    return logging.getLogger(name)


# Each helper calls utils.create_logger_record directly (rather than going
# through log()) so that the caller can be found at a fixed stack depth.
def log(level, message, *args, **kwargs):
    utils.create_logger_record(level, message, *args, **kwargs)


def debug(message, *args, **kwargs):
    utils.create_logger_record(logging.DEBUG, message, *args, **kwargs)


def info(message, *args, **kwargs):
    utils.create_logger_record(logging.INFO, message, *args, **kwargs)


def warning(message, *args, **kwargs):
    utils.create_logger_record(logging.WARNING, message, *args, **kwargs)


def error(message, *args, **kwargs):
    utils.create_logger_record(logging.ERROR, message, *args, **kwargs)


def critical(message, *args, **kwargs):
    utils.create_logger_record(logging.CRITICAL, message, *args, **kwargs)


fatal = critical


def exception(message, *args, exc_info=True, **kwargs):
    utils.create_logger_record(
        logging.ERROR, message, *args, exc_info=exc_info, **kwargs
    )
