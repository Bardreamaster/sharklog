import logging

import pytest

import sharklog
from sharklog import settings, utils


@pytest.mark.parametrize(
    "value, expected",
    [
        (logging.DEBUG, logging.DEBUG),
        (15, 15),
        ("debug", logging.DEBUG),
        ("Info", logging.INFO),
        ("WARNING", logging.WARNING),
        ("warn", logging.WARNING),
        (" error ", logging.ERROR),
        ("critical", logging.CRITICAL),
        ("25", 25),
    ],
)
def test_parse_level(value, expected):
    assert utils.parse_level(value) == expected


@pytest.mark.parametrize("value", ["verbose", "", None, 1.5])
def test_parse_level_rejects_unknown(value):
    with pytest.raises(ValueError, match="Unknown level"):
        utils.parse_level(value)


def test_init_accepts_level_names():
    assert sharklog.init("test_levels.init", level="debug").level == logging.DEBUG
    assert sharklog.init("test_levels.init", level="error").level == logging.ERROR


def test_init_default_and_debug_flag():
    assert sharklog.init("test_levels.default").level == settings.DEFAULT_LEVEL
    logger = sharklog.init("test_levels.flag", debug=True, level="error")
    assert logger.level == logging.DEBUG


def test_init_rejects_unknown_level():
    with pytest.raises(ValueError, match="Unknown level"):
        sharklog.init("test_levels.bad", level="verbose")


def test_reset_all_accepts_level_names(monkeypatch):
    monkeypatch.setattr(settings, "DEFAULT_LEVEL", settings.DEFAULT_LEVEL)
    sharklog.reset_all(level="warning")
    assert settings.DEFAULT_LEVEL == logging.WARNING
    assert logging.root.level == logging.WARNING
