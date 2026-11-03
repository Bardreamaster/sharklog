import io
import logging

import pytest

import sharklog
from sharklog import settings


@pytest.fixture(autouse=True)
def keep_default_level(monkeypatch):
    monkeypatch.setattr(settings, "DEFAULT_LEVEL", settings.DEFAULT_LEVEL)


def test_repeated_reset_all_updates_level_and_format():
    stream = io.StringIO()
    logging.root.handlers[:] = [logging.StreamHandler(stream)]

    sharklog.reset_all()
    assert logging.root.level == logging.INFO

    sharklog.reset_all(debug=True, format="%(levelname)s:%(message)s")
    assert logging.root.level == logging.DEBUG
    logging.getLogger("test_reset_all").debug("now visible")
    assert stream.getvalue() == "DEBUG:now visible\n"


def test_reset_all_configures_root_handler(run_python):
    proc = run_python(
        {"main.py": """
                import logging
                import sharklog

                sharklog.reset_all(debug=True, format="%(name)s %(message)s")
                logging.getLogger("lib").debug("hello")
            """},
        ["main.py"],
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr == "lib hello\n"
