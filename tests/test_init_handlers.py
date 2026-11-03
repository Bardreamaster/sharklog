import io
import logging

import sharklog


def test_init_twice_does_not_duplicate_output(run_python):
    proc = run_python(
        {"main.py": """
                import sharklog

                sharklog.init()
                sharklog.init()
                sharklog.info("hello")
            """},
        ["main.py"],
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr.count("hello") == 1


def test_reinit_applies_new_settings(run_python):
    proc = run_python(
        {"main.py": """
                import sharklog

                sharklog.init()
                sharklog.debug("hidden")
                sharklog.init(debug=True, format="NEW %(levelname)s %(message)s")
                sharklog.debug("shown")
            """},
        ["main.py"],
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr.splitlines() == ["NEW DEBUG shown"]


def test_init_keeps_user_handlers():
    logger = sharklog.init("test_init_handlers.user")
    stream = io.StringIO()
    user_handler = logging.StreamHandler(stream)
    logger.addHandler(user_handler)

    logger = sharklog.init("test_init_handlers.user")

    assert user_handler in logger.handlers
    assert len(logger.handlers) == 2
