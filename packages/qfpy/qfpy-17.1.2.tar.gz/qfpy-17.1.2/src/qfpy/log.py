"""
logger
"""

import sys

from loguru import logger

logger.configure(
    handlers=[
        dict(
            sink=sys.stderr,
            format="<green>{time:HH:mm:ss.SSS}</green> <cyan>{file}</cyan>:<cyan>{line}</cyan> <level>{message}</level>",
        )
    ]
)
