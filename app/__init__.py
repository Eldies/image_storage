# -*- coding: utf-8 -*-
from logging.config import dictConfig

from .logging_config import LogConfig

dictConfig(LogConfig().dict())
