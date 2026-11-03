import dataclasses
import inspect
import io
import logging
import sys
import traceback
from pprint import pformat
from typing import Dict, Tuple


def create_logger_record(
    level,
    message,
    *args,
    name: str = "",
    exc_info=None,
    extra=None,
    stack_info: bool = False,
    stacklevel=1,
    **kwargs,
) -> bool:
    """Create and dispatch a record on behalf of a public sharklog function.

    Must be called directly from the public function (``sharklog.info`` etc.).
    ``exc_info``, ``extra``, ``stack_info`` and ``stacklevel`` behave like in
    the standard library; ``stacklevel=1`` attributes the record to the code
    calling that public function. Any other keyword argument is added to the
    record as an extra attribute, like an ``extra`` entry.
    """
    frame = _caller_frame(stacklevel + 1)

    name, parent_name = parse_name(name, frame.f_globals)
    logger = get_logger(name, parent_name)
    if not logger.isEnabledFor(level):
        return False

    record = logger.makeRecord(
        name,
        level,
        fn=parse_filename(frame.f_globals),
        lno=frame.f_lineno,
        msg=format_message(message),
        args=args,
        exc_info=normalize_exc_info(exc_info),
        func=frame.f_code.co_name,
        extra={**kwargs, **(extra or {})},
        sinfo=format_stack(frame) if stack_info else None,
    )
    logger.handle(record)
    return True


def normalize_exc_info(exc_info):
    """Accept the same ``exc_info`` values as the standard library."""
    if not exc_info:
        return None
    if isinstance(exc_info, BaseException):
        return (type(exc_info), exc_info, exc_info.__traceback__)
    if isinstance(exc_info, tuple):
        return exc_info
    return sys.exc_info()


def format_stack(frame) -> str:
    stream = io.StringIO()
    stream.write("Stack (most recent call last):\n")
    traceback.print_stack(frame, file=stream)
    return stream.getvalue().rstrip("\n")


def _caller_frame(depth: int):
    """Return the frame ``depth`` levels above the caller of this function.

    Like the standard library, an out-of-range depth falls back to the
    outermost frame instead of failing.
    """
    frame = inspect.currentframe().f_back  # the function calling us
    for _ in range(depth):
        if frame.f_back is None:
            break
        frame = frame.f_back
    return frame


def parse_name(custom_name: str, frame_info: Dict) -> Tuple[str, str]:
    module_name = custom_name or frame_info["__name__"]
    if module_name == "__main__":
        try:
            module_name = frame_info["__file__"].split(".")[0].replace("/", ".")
        except KeyError:
            module_name = "interactive"
    parent_module_name = module_name.split(".")[0]
    return module_name, parent_module_name


def get_logger(name: str, parent_name: str):
    logger = logging.getLogger(name)
    if not logger.level:
        parent_logger = logging.getLogger(parent_name)
        logger.level = parent_logger.level
    if not logger.level:
        logger.level = logging.root.level
    return logger


def parse_filename(frame_info: Dict) -> str:
    return frame_info.get("__file__", "interactive")


def format_message(value) -> str:
    if dataclasses.is_dataclass(value):
        value = dataclasses.asdict(value)
    if not isinstance(value, str):
        value = pformat(value)
    return value
