import pytest

# Every entry point initialises its logger and reports the names seen by
# init(), getLogger() and the module-level helpers; they must all agree.
PROBE = """
import logging as std_logging
import sharklog

names = {
    sharklog.init(debug=True, format="%(name)s|%(message)s").name,
    sharklog.getLogger().name,
}
print("|".join(sorted(names)))
sharklog.debug("debug works")
"""


@pytest.mark.parametrize(
    "files, args, expected",
    [
        ({"script.py": PROBE}, ["script.py"], "script"),
        ({"sub/dir/script.py": PROBE}, ["sub/dir/script.py"], "script"),
        (
            {"app/__init__.py": "", "app/__main__.py": PROBE},
            ["-m", "app"],
            "app.__main__",
        ),
        (
            {"pkg/__init__.py": "", "pkg/tool.py": PROBE},
            ["-m", "pkg.tool"],
            "pkg.tool",
        ),
        ({}, ["-c", PROBE], "interactive"),
    ],
)
def test_entry_point_names_are_consistent(run_python, files, args, expected):
    proc = run_python(files, args)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == expected
    assert proc.stderr.splitlines() == [f"{expected}|debug works"]


def test_imported_module_uses_its_module_name(run_python):
    proc = run_python(
        {
            "pkg/__init__.py": "",
            "pkg/mod.py": """
                import sharklog

                logger = sharklog.getLogger()
            """,
            "main.py": """
                from pkg import mod

                print(mod.logger.name)
            """,
        },
        ["main.py"],
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "pkg.mod"


def test_explicit_name_wins():
    import sharklog

    assert sharklog.getLogger("custom.name").name == "custom.name"
    assert sharklog.init("custom.other").name == "custom.other"
