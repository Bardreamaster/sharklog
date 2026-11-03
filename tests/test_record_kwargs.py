def run_main(run_python, fmt, body):
    source = (
        "import sharklog\n"
        f"sharklog.init(debug=True, format={fmt!r})\n"
        "def fail():\n"
        "    raise ValueError('bad value')\n"
    )
    proc = run_python({"main.py": source + body}, ["main.py"])
    assert proc.returncode == 0, proc.stderr
    assert "Logging error" not in proc.stderr, proc.stderr
    return proc.stderr


def test_extra_dict_sets_record_attributes(run_python):
    out = run_main(
        run_python,
        "%(user)s %(message)s",
        "sharklog.info('hi', extra={'user': 'alice'})\n",
    )
    assert out == "alice hi\n"


def test_extra_keyword_arguments_still_supported(run_python):
    out = run_main(
        run_python, "%(user)s %(message)s", "sharklog.info('hi', user='bob')\n"
    )
    assert out == "bob hi\n"


def test_exc_info_true(run_python):
    out = run_main(
        run_python,
        "%(message)s",
        "try:\n    fail()\nexcept ValueError:\n    sharklog.error('boom', exc_info=True)\n",
    )
    assert out.startswith("boom\nTraceback (most recent call last):")
    assert "ValueError: bad value" in out


def test_exc_info_exception_instance(run_python):
    out = run_main(
        run_python,
        "%(message)s",
        "try:\n    fail()\nexcept ValueError as e:\n    err = e\n"
        "sharklog.warning('later', exc_info=err)\n",
    )
    assert out.startswith("later\nTraceback")
    assert "ValueError: bad value" in out


def test_exception_logs_traceback(run_python):
    out = run_main(
        run_python,
        "%(levelname)s %(message)s",
        "try:\n    fail()\nexcept ValueError:\n    sharklog.exception('caught')\n",
    )
    assert out.startswith("ERROR caught\nTraceback")
    assert "ValueError: bad value" in out


def test_exception_without_traceback(run_python):
    out = run_main(
        run_python,
        "%(message)s",
        "try:\n    fail()\nexcept ValueError:\n    sharklog.exception('quiet', exc_info=False)\n",
    )
    assert out == "quiet\n"


def test_stack_info(run_python):
    out = run_main(
        run_python,
        "%(message)s",
        "def where():\n    sharklog.info('here', stack_info=True)\nwhere()\n",
    )
    assert out.startswith("here\nStack (most recent call last):")
    assert "in where" in out
    assert "create_logger_record" not in out
