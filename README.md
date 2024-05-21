# sharklog

Python logging helper.

[![PyPI License](https://img.shields.io/pypi/l/sharklog.svg)](https://pypi.org/project/sharklog)
[![PyPI Version](https://img.shields.io/pypi/v/sharklog.svg)](https://pypi.org/project/sharklog)

## Quick Start

- Install sharklog:

```bash
python -m pip install sharklog
```

- Use in standalone script:

```python
# standalone.py
from sharklog import logging

logging.init(debug=True)
logging.debug("debug message")
logging.info("info message")
logging.warning("warning message")
logging.error("error message")
```

- Use in module:

```python
# submodule.py which is placed under package `parent`
from sharklog import logging

logger = logging.getLogger()    # the logger name will be `parent.submodule`

logger.debug("debug message")
logger.info("info message")
logger.warning("warning message")
logger.error("error message")
```

If you already using builtin logging module, you can use sharklog as a drop-in replacement.

Just change ~~`import logging`~~ into `from sharklog import logging`. Then you can use `logging` as usual:

```python
# module_name.py
from sharklog import logging

# these log messages will be prefixed with the logger name `xxxpackage.xxmodule.module_name`
logging.debug("debug message")
logging.info("info message")
logging.warning("warning message")
logging.error("error message")
```

## Usage in Package Development

```python
# parent/__init__.py
from sharklog import logging

logging.getLogger().addHandler(logging.NullHandler())
```
