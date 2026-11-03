import dataclasses
import inspect
import logging
from pprint import pformat
from typing import Dict, Tuple


def create_logger_record(
    level, message, *args, name: str = "", exc_info=None, **kwargs
) -> bool:
    frame = inspect.currentframe().f_back.f_back.f_back  # type: ignore
    assert frame

    name, _ = parse_name(name, frame.f_globals)
    # Plain getLogger: level and handlers are inherited through the standard
    # logger hierarchy (e.g. from a package logger configured with init()).
    logger = logging.getLogger(name)
    if not logger.isEnabledFor(level):
        return False

    record = logger.makeRecord(
        name,
        level,
        fn=parse_filename(frame.f_globals),
        lno=frame.f_lineno,
        msg=format_message(message),
        args=args,
        exc_info=exc_info,
        extra=kwargs,
        sinfo=None,
    )
    logger.handle(record)
    return True


def parse_name(custom_name: str, frame_info: Dict) -> Tuple[str, str]:
    module_name = custom_name or resolve_name(frame_info)
    parent_module_name = module_name.split(".")[0]
    return module_name, parent_module_name


def parse_filename(frame_info: Dict) -> str:
    return frame_info.get("__file__", "interactive")


def resolve_name(frame_info: Dict) -> str:
    """Logger name for the module whose globals are ``frame_info``.

    Imported modules use their ``__name__``. For the entry point
    (``__name__ == "__main__"``) a more useful name is derived:

    - ``python -m pkg.tool``: the real module name, ``pkg.tool``
      (``pkg.__main__`` for ``python -m pkg``);
    - ``python path/to/script.py``: the file name, ``script``;
    - interactive sessions / ``python -c``: ``interactive``.
    """
    name = frame_info.get("__name__") or "interactive"
    if name != "__main__":
        return name
    spec = frame_info.get("__spec__")
    if spec is not None and spec.name:
        return spec.name
    file_name = frame_info.get("__file__")
    if file_name:
        return inspect.getmodulename(file_name) or "__main__"
    return "interactive"


def format_message(value) -> str:
    if dataclasses.is_dataclass(value):
        value = dataclasses.asdict(value)
    if not isinstance(value, str):
        value = pformat(value)
    return value


def parse_level(level) -> int:
    """Convert a level number or a case-insensitive name ("debug") to an int."""
    if isinstance(level, int):
        return level
    if isinstance(level, str):
        name = level.strip().upper()
        if name.isdigit():
            return int(name)
        value = logging.getLevelName(name)
        if isinstance(value, int):
            return value
    raise ValueError(f"Unknown level: {level!r}")
