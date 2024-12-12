# sharklog

Python logging helper.

[![PyPI License](https://img.shields.io/pypi/l/sharklog.svg)](https://pypi.org/project/sharklog)
[![PyPI Version](https://img.shields.io/pypi/v/sharklog.svg)](https://pypi.org/project/sharklog)

## Quick Start

- Install sharklog:

```bash
python3 -m pip install sharklog
```

- Use in standalone script:

```python
# standalone.py
import sharklog

sharklog.init(debug=True)    # init current logger with level=sharklog.DEBUG

sharklog.debug("debug message")
sharklog.info("info message")
sharklog.warning("warning message")
sharklog.error("error message")
```

The default format of log messages is:

```python
"[%(levelname)s]: %(message)s [%(asctime)s](%(filename)s:%(lineno)d)"
```

## Usage

### Use in standalone script

If you want to change logging level for a module, you can set it in the module by:

```python
import sharklog
sharklog.getLogger().setLevel(logging.DEBUG)
```

or set it outside the module by specifying the logger name:

```python
import sharklog
sharklog.getLogger("module_name").setLevel(logging.DEBUG)
```

### Usage in Package Development

Now I assume your file structure is like this:

```bash
--- parent_package
    |--- __init__.py
    |--- parent_module.py
    |--- logger.py
    |--- sub_package
        |--- __init__.py
        |--- sub_module.py
```

- First, you can add `NullHandler` to the root logger in `parent_package/__init__.py`, which logger named `parent_package`:

```python
# parent/__init__.py
from sharklog import logging

logging.getLogger().addHandler(logging.NullHandler())
```

This is mentioned in the [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library) to identify the logger's default behavior.

- Then, use `logging` in your package, they will be prefixed with the logger name `parent_package.`:

```python
# parent_module.py which is placed under package `parent_package`
from sharklog import logging

logger = logging.getLogger()    # the logger name will be `parent_package.parent_module`

logger.debug("debug message")
logger.info("info message")
logger.warning("warning message")
logger.error("error message")
```

If you already using builtin logging module, you can use sharklog as a drop-in replacement.

Just change ~~`import logging`~~ into `from sharklog import logging`. Then you can use `logging` as usual:

```python
# sub_module.py
from sharklog import logging

# these log messages will be prefixed with the logger name `xxxpackage.xxmodule.module_name`
# here, as an example, the logger name will be `parent_package.sub_package.sub_module`
logging.debug("debug message")
logging.info("info message")
logging.warning("warning message")
logging.error("error message")
```

- Finally, you can set the logging level for the package in the main script which using the package:

```python
# main.py
from sharklog import logging

from parent_package import parent_module
from parent_package.sub_package import sub_module

if __name__ == "__main__":
    logging.init(debug=True)    # init current logger with level=logging.DEBUG
    # or logging.init(level=logging.DEBUG)
    # logging inside the package will use the level set here
```

Or if you want to change the logging level for a specific module, you can set it in the module by:

```python
from sharklog import logging
logging.getLogger().setLevel(logging.WARNING)
```
