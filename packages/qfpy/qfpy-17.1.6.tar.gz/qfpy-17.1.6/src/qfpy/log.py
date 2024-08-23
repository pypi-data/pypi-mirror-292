"""
logger
"""

import sys

from loguru import logger

logger.configure(
    handlers=[
        dict(
            sink=sys.stderr,
            format="<green>{time:HH:mm:ss.SSS}</green> <cyan>{file}</cyan>:<cyan>{line}</cyan> <m>{function}</m> <level>{message}</level>",
        )
    ]
)

if __name__ == "__main__":
    logger.debug("debug message")
    logger.info("info message")