import sharklog

sharklog.init(debug=True)  # init current logger with level=sharklog.DEBUG

sharklog.debug("debug message")

sharklog.info("info message")
sharklog.warning("warning message")
sharklog.error("error message")
