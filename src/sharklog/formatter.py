import logging

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


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        level_color = LEVEL_COLORS.get(record.levelno, COLOR_RESET)
        record.levelname = f"{level_color}{record.levelname}{COLOR_RESET}"
        return super().format(record)
