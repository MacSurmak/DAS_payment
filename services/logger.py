import logging
import sys
from typing import List, Union

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logger(level: Union[str, int] = "INFO", ignored: List[str] = ""):
    # 1. Remove the default loguru handler and add a new one with our level
    logger.remove()
    logger.add(sys.stderr, level=level)

    # 2. Configure the standard logging library to be intercepted
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 3. Mute noisy loggers from libraries
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)

    # 4. Disable loggers if needed
    for ignore in ignored:
        logger.disable(ignore)

    logger.info("Logging is successfully configured")
