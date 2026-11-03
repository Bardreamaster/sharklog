import logging
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


@pytest.fixture
def run_python(tmp_path):
    """Write ``files`` into a temp project and run Python there.

    sharklog derives logger names and caller info from the calling module,
    so most behaviour is best exercised in a fresh interpreter.

    ``files`` maps relative paths to source code; ``args`` are passed to the
    interpreter (e.g. ``["main.py"]`` or ``["-m", "app"]``).
    Returns the CompletedProcess with ANSI color codes stripped from stderr.
    """

    def _run(files, args, env=None):
        for rel_path, source in files.items():
            path = tmp_path / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(textwrap.dedent(source))
        full_env = {
            **os.environ,
            "PYTHONPATH": os.pathsep.join([str(SRC_DIR), str(tmp_path)]),
        }
        full_env.update(env or {})
        proc = subprocess.run(
            [sys.executable, *args],
            cwd=tmp_path,
            env=full_env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        proc.raw_stderr = proc.stderr
        proc.stderr = strip_ansi(proc.stderr)
        return proc

    return _run


@pytest.fixture(autouse=True)
def isolate_logging():
    """Restore global logging state after in-process tests."""
    manager = logging.root.manager
    saved = {
        name: (lg.level, list(lg.handlers), lg.propagate)
        for name, lg in manager.loggerDict.items()
        if isinstance(lg, logging.Logger)
    }
    root_state = (logging.root.level, list(logging.root.handlers))
    yield
    for name, lg in list(manager.loggerDict.items()):
        if not isinstance(lg, logging.Logger):
            continue
        level, handlers, propagate = saved.get(name, (logging.NOTSET, [], True))
        lg.setLevel(level)
        lg.handlers[:] = handlers
        lg.propagate = propagate
    logging.root.setLevel(root_state[0])
    logging.root.handlers[:] = root_state[1]
