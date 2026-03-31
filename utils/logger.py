from loguru import logger

logger.add("log/log.log", rotation="1 MB")

# Экспортируем логгер для использования в других модулях
__all__ = ["logger"]
