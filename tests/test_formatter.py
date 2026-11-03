import io
import logging

from sharklog.formatter import COLOR_GREEN, COLOR_RESET, ColoredFormatter


def make_handler(formatter):
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    return handler, stream


def test_levelname_is_colored():
    handler, stream = make_handler(ColoredFormatter("%(levelname)s %(message)s"))
    logger = logging.getLogger("test_formatter.colored")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.warning("x")
    logger.info("y")
    assert stream.getvalue().splitlines()[1] == f"{COLOR_GREEN}INFO{COLOR_RESET} y"


def test_color_does_not_leak_into_other_handlers():
    logger = logging.getLogger("test_formatter.leak")
    logger.setLevel(logging.INFO)
    colored, colored_stream = make_handler(
        ColoredFormatter("%(levelname)s %(message)s")
    )
    plain, plain_stream = make_handler(logging.Formatter("%(levelname)s %(message)s"))
    logger.addHandler(colored)
    logger.addHandler(plain)

    logger.info("hello")

    assert plain_stream.getvalue() == "INFO hello\n"
    assert colored_stream.getvalue() == f"{COLOR_GREEN}INFO{COLOR_RESET} hello\n"


def test_color_is_not_applied_twice():
    logger = logging.getLogger("test_formatter.twice")
    logger.setLevel(logging.INFO)
    first, first_stream = make_handler(ColoredFormatter("%(levelname)s"))
    second, second_stream = make_handler(ColoredFormatter("%(levelname)s"))
    logger.addHandler(first)
    logger.addHandler(second)

    logger.info("hello")

    expected = f"{COLOR_GREEN}INFO{COLOR_RESET}\n"
    assert first_stream.getvalue() == expected
    assert second_stream.getvalue() == expected


def test_custom_level_is_left_uncolored():
    logger = logging.getLogger("test_formatter.custom")
    logger.setLevel(1)
    handler, stream = make_handler(ColoredFormatter("%(levelname)s"))
    logger.addHandler(handler)
    logger.log(25, "custom")
    assert stream.getvalue() == "Level 25\n"
