def test_standalone_script_debug(run_python):
    proc = run_python(
        {"standalone.py": """
                import sharklog

                sharklog.init(debug=True)
                sharklog.debug("debug message")
                sharklog.info("info message")
                sharklog.warning("warning message")
                sharklog.error("error message")
            """},
        ["standalone.py"],
    )
    assert proc.returncode == 0, proc.stderr
    lines = proc.stderr.splitlines()
    assert len(lines) == 4
    for level, line in zip(["DEBUG", "INFO", "WARNING", "ERROR"], lines):
        assert line.startswith(f"[{level}]: {level.lower()} message [")
        assert "(standalone.py:" in line


def test_default_level_hides_debug(run_python):
    proc = run_python(
        {"standalone.py": """
                import sharklog

                sharklog.init()
                sharklog.debug("hidden")
                sharklog.info("shown")
            """},
        ["standalone.py"],
    )
    assert proc.returncode == 0, proc.stderr
    assert "hidden" not in proc.stderr
    assert "[INFO]: shown" in proc.stderr
