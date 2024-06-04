from pydantic.v1 import BaseModel


class LogConfig(BaseModel):
    """Logging configuration"""

    LOGGER_NAME: str = "image-storage"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s.%(msecs)03d | %(name)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": True,
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        LOGGER_NAME: {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    }
    loggers = {
        LOGGER_NAME: {"handlers": [LOGGER_NAME], "level": LOG_LEVEL},
        "uvicorn": {"handlers": [LOGGER_NAME], "level": "INFO"},
    }
