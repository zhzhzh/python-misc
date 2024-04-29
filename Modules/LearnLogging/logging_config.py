LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(funcName)s:%(lineno)s] %(message)s"
        },
        "simple": {"format": "[%(levelname)s] %(message)s"},
    },
    "handlers": {
        "null": {"level": "DEBUG", "class": "logging.NullHandler"},
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "verbose",
        },
        "info_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "verbose",
            "filename": "info.log",
            "when": "midnight",
            "backupCount": 7,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "root": {"handlers": ["console"], "level": "INFO"},
        "LearnLogging": {
            "handlers": ["console", "info_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
