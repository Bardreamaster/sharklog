import logging as std_logging

from sharklog import logging


def test_stdlib_names_are_available():
    for name in std_logging.__all__:
        assert hasattr(logging, name), name
    assert logging.DEBUG == std_logging.DEBUG
    assert logging.NullHandler is std_logging.NullHandler
    assert logging.Logger is std_logging.Logger


def test_sharklog_helpers_shadow_stdlib():
    import sharklog.logging as sharklog_logging

    for name in ["getLogger", "debug", "info", "warning", "error", "critical"]:
        assert getattr(logging, name) is getattr(sharklog_logging, name)
        assert getattr(logging, name) is not getattr(std_logging, name)
    assert callable(logging.init)
    assert callable(logging.reset_all)


def test_readme_package_usage(run_python):
    proc = run_python(
        {
            "parent_package/__init__.py": """
                from sharklog import logging

                logging.getLogger().addHandler(logging.NullHandler())
            """,
            "main.py": """
                from sharklog import logging

                import parent_package  # noqa: F401

                if __name__ == "__main__":
                    logging.init(level=logging.DEBUG)
                    logging.debug("main debug")
                    logging.getLogger().setLevel(logging.WARNING)
                    logging.info("hidden")
            """,
        },
        ["main.py"],
    )
    assert proc.returncode == 0, proc.stderr
    assert "[DEBUG]: main debug" in proc.stderr
    assert "hidden" not in proc.stderr
