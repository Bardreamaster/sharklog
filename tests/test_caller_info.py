import pytest

FORMAT = "%(levelname)s|%(filename)s:%(lineno)d|%(funcName)s|%(message)s"


def run_main(run_python, body):
    source = (
        "\n"
        "import sharklog\n"
        "from sharklog import logging\n"
        "\n"
        f'sharklog.init(level=1, format="{FORMAT}")\n'
    )
    proc = run_python({"main.py": source + body}, ["main.py"])
    assert proc.returncode == 0, proc.stderr
    return proc.stderr.splitlines()


@pytest.mark.parametrize(
    "call",
    [
        "sharklog.debug('m')",
        "sharklog.info('m')",
        "sharklog.warning('m')",
        "sharklog.error('m')",
        "sharklog.critical('m')",
        "sharklog.fatal('m')",
        "sharklog.exception('m')",
        "sharklog.log(25, 'm')",
        "logging.log(25, 'm')",
    ],
)
def test_module_level_call_reports_caller(run_python, call):
    lines = run_main(run_python, f"{call}\n")
    assert len(lines) >= 1
    assert lines[0].split("|")[1:] == ["main.py:6", "<module>", "m"]


def test_call_inside_function_reports_function(run_python):
    lines = run_main(
        run_python,
        """
def work():
    sharklog.info("in work")
    sharklog.log(30, "log in work")

work()
""",
    )
    assert lines == [
        "INFO|main.py:8|work|in work",
        "WARNING|main.py:9|work|log in work",
    ]


def test_stacklevel_attributes_record_to_wrapper_caller(run_python):
    lines = run_main(
        run_python,
        """
def my_log(msg):
    sharklog.info(msg, stacklevel=2)

def caller():
    my_log("wrapped")

caller()
""",
    )
    assert lines == ["INFO|main.py:11|caller|wrapped"]


def test_top_level_log_and_fatal_use_sharklog():
    import sharklog
    import sharklog.logging

    assert sharklog.log is sharklog.logging.log
    assert sharklog.fatal is sharklog.logging.critical
