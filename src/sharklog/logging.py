import inspect
import logging
import sys

from sharklog import settings, utils
from sharklog.formatter import ColoredFormatter


def init(name: str = None, debug: bool = False, level=None, **kwargs):
    kwargs["level"] = kwargs.get("level", settings.DEFAULT_LEVEL)
    if debug:
        kwargs["level"] = logging.DEBUG
    elif level is not None:
        try:
            kwargs["level"] = level
        except KeyError:
            kwargs["level"] = logging.DEBUG

    kwargs["format"] = kwargs.get("format", settings.DEFAULT_FORMAT)

    custom_format = kwargs.get("format")
    formatter = ColoredFormatter(
        fmt=custom_format,
        datefmt=kwargs.get("datefmt"),
        style=kwargs.get("style", "%"),
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    frame = inspect.currentframe().f_back
    if not name:
        name = frame.f_globals["__name__"]
        if name == "__main__":
            try:
                name = frame.f_globals["__file__"].split(".")[0].replace("/", ".")
            except KeyError:
                name = "interactive"
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(kwargs["level"])
    return logger


def reset_all(debug=False, level=None, **kwargs):
    if debug:
        settings.DEFAULT_LEVEL = logging.DEBUG
    elif level is not None:
        try:
            settings.DEFAULT_LEVEL = level
        except KeyError:
            settings.DEFAULT_LEVEL = logging.DEBUG

    kwargs["level"] = kwargs.get("level", settings.DEFAULT_LEVEL)
    kwargs["format"] = kwargs.get("format", settings.DEFAULT_FORMAT)
    logging.basicConfig(**kwargs)

    custom_format = kwargs.get("format")
    if custom_format:
        formatter = logging.Formatter(
            fmt=custom_format,
            datefmt=kwargs.get("datefmt"),
            style=kwargs.get("style", "%"),
        )
        for handler in logging.root.handlers:
            handler.setFormatter(formatter)


def getLogger(name=None):
    if not name:
        frame = inspect.currentframe().f_back
        name = frame.f_globals["__name__"]
        if name == "__main__":
            try:
                name = frame.f_globals["__file__"].split(".")[0].replace("/", ".")
            except KeyError:
                name = "interactive"
    return logging.getLogger(name)


def log(level, message, *args, **kwargs):
    utils.create_logger_record(level, message, *args, **kwargs)


def debug(message, *args, **kwargs):
    log(logging.DEBUG, message, *args, **kwargs)


def info(message, *args, **kwargs):
    log(logging.INFO, message, *args, **kwargs)


def warning(message, *args, **kwargs):
    log(logging.WARNING, message, *args, **kwargs)


def error(message, *args, **kwargs):
    log(logging.ERROR, message, *args, **kwargs)


def critical(message, *args, **kwargs):
    log(logging.CRITICAL, message, *args, **kwargs)


def exception(message, *args, **kwargs):
    kwargs["exc_info"] = kwargs.get("exc_info", sys.exc_info())
    log(logging.ERROR, message, *args, **kwargs)
