import logging
import traceback
import sys
from pathlib import Path

# Location for logs
BASE_DIR = Path(__file__).resolve().parents[3]
LOGS_DIR = Path(BASE_DIR, "logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# logging config
logging_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    # FORMATTERS
    "formatters": {
        "minimal": {"format": "[%(levelname)s] %(message)s"},
        "detailed": {
            "format": "[%(levelname)s] %(asctime)s:%(filename)s:%(funcName)s:\
            \nline %(lineno)d:%(message)s"
        },
    },
    # HANDLERS
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "minimal",
            "level": logging.INFO,
        },
        "mainloader": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Path(LOGS_DIR, "mainloader.log"),
            "formatter": "detailed",
            "level": logging.DEBUG,
            "backupCount": 5,
            "maxBytes": 10485760,  # 1 MB
        },
    },
    # LOGGERS
    "loggers": {
        "": {
            "handlers": ["console", "mainloader"],
            "level": logging.DEBUG,
            "propagate": True,
        }
    },
}


# Decorator function for logging traceback exception
def log_exception(logger):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                logger.error(traceback.format_exc())
                raise

        return wrapper

    return decorator
