PACKAGE = {
    "parent_package/__init__.py": """
        import logging

        logging.getLogger(__name__).addHandler(logging.NullHandler())
    """,
    "parent_package/sub_package/__init__.py": "",
    "parent_package/sub_package/sub_module.py": """
        import sharklog

        def run(tag):
            sharklog.debug(f"pkg debug {tag}")
            sharklog.info(f"pkg info {tag}")
            sharklog.warning(f"pkg warning {tag}")
    """,
}


def run_main(run_python, body):
    files = {
        **PACKAGE,
        "main.py": "from parent_package.sub_package import sub_module\n" + body,
    }
    proc = run_python(files, ["main.py"])
    assert proc.returncode == 0, proc.stderr
    return [line.split(" [")[0] for line in proc.stderr.splitlines()]


def test_package_logger_configures_submodules(run_python):
    lines = run_main(
        run_python,
        """
import sharklog
sharklog.init("parent_package", debug=True)
sub_module.run("a")
""",
    )
    assert lines == [
        "[DEBUG]: pkg debug a",
        "[INFO]: pkg info a",
        "[WARNING]: pkg warning a",
    ]


def test_level_is_not_frozen_by_early_logging(run_python):
    lines = run_main(
        run_python,
        """
import logging
import sharklog
sub_module.run("before")          # logged before the package is configured
pkg_logger = sharklog.init("parent_package", level=logging.WARNING)
sub_module.run("warning")
pkg_logger.setLevel(logging.DEBUG)
sub_module.run("debug")
""",
    )
    assert lines == [
        "[WARNING]: pkg warning warning",
        "[DEBUG]: pkg debug debug",
        "[INFO]: pkg info debug",
        "[WARNING]: pkg warning debug",
    ]


def test_intermediate_logger_level_is_respected(run_python):
    lines = run_main(
        run_python,
        """
import logging
import sharklog
sharklog.init("parent_package", debug=True)
logging.getLogger("parent_package.sub_package").setLevel(logging.WARNING)
sub_module.run("x")
""",
    )
    assert lines == ["[WARNING]: pkg warning x"]
