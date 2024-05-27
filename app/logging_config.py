from pydantic.v1 import BaseModel


class LogConfig(BaseModel):
    """Logging configuration"""

    LOGGER_NAME: str = "image-storage"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(name)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "image-storage": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    }
    loggers = {
        "image-storage": {"handlers": ["image-storage"], "level": LOG_LEVEL},
        "update_db": {"handlers": ["image-storage"], "level": LOG_LEVEL},
    }
