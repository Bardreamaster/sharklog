import logging
import os

COLOR_RESET = "\033[0m"
COLOR_RED = "\033[31m"
COLOR_CHERRY = "\033[91m"
COLOR_YELLOW = "\033[33m"
COLOR_GREEN = "\033[32m"
COLOR_BLUE = "\033[34m"

LEVEL_COLORS = {
    logging.DEBUG: COLOR_BLUE,
    logging.INFO: COLOR_GREEN,
    logging.WARNING: COLOR_YELLOW,
    logging.ERROR: COLOR_RED,
    logging.CRITICAL: COLOR_CHERRY,
}


def supports_color(stream) -> bool:
    """Whether ANSI colors should be written to ``stream``.

    Honours the NO_COLOR (https://no-color.org) and FORCE_COLOR conventions,
    otherwise colors are only used when the stream is a terminal, so that
    redirected output (files, pipes, CI logs) stays free of escape codes.
    """
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    isatty = getattr(stream, "isatty", None)
    try:
        return bool(isatty and isatty())
    except ValueError:  # closed stream
        return False


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        level_color = LEVEL_COLORS.get(record.levelno, COLOR_RESET)
        record.levelname = f"{level_color}{record.levelname}{COLOR_RESET}"
        return super().format(record)
