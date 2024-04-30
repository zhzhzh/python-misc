import os
from logging.config import dictConfig

from Utils.env_util import get_log_folder

LOCAL_LOGGING = {
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
        "debug_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "verbose",
            "filename": os.path.join(get_log_folder(), "debug.log"),
            "when": "midnight",
            "backupCount": 7,
            "encoding": "utf8",
        },
        "error_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "ERROR",
            "formatter": "verbose",
            "filename": os.path.join(get_log_folder(), "error.log"),
            "when": "midnight",
            "backupCount": 7,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "root": {"handlers": ["console"], "level": "INFO"},
        "__main__": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "Utils": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "LearnLogging": {
            "handlers": ["console", "debug_file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


def config_local_logger() -> None:
    dictConfig(LOCAL_LOGGING)
