import io

import pytest

from sharklog.formatter import COLOR_RESET, supports_color

SCRIPT = {"main.py": """
        import sharklog

        sharklog.init()
        sharklog.info("hello")
    """}


class FakeTTY(io.StringIO):
    def isatty(self):
        return True


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("FORCE_COLOR", raising=False)


def test_supports_color_detection(monkeypatch):
    assert supports_color(FakeTTY()) is True
    assert supports_color(io.StringIO()) is False
    assert supports_color(object()) is False
    monkeypatch.setenv("NO_COLOR", "1")
    assert supports_color(FakeTTY()) is False
    monkeypatch.delenv("NO_COLOR")
    monkeypatch.setenv("FORCE_COLOR", "1")
    assert supports_color(io.StringIO()) is True


def test_no_color_when_output_is_redirected(run_python):
    proc = run_python(SCRIPT, ["main.py"])
    assert proc.returncode == 0, proc.raw_stderr
    assert COLOR_RESET not in proc.raw_stderr
    assert "[INFO]: hello" in proc.raw_stderr


def test_force_color(run_python):
    proc = run_python(SCRIPT, ["main.py"], env={"FORCE_COLOR": "1"})
    assert proc.returncode == 0, proc.raw_stderr
    assert COLOR_RESET in proc.raw_stderr
