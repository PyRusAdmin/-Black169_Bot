# -*- coding: utf-8 -*-
from loguru import logger

logger.add("log/log.log", rotation="1 MB")
