"""
Logging configuration for BrandPhantom.
"""

import logging
import sys

from config.settings import settings


def setup_logging():
    """Configures structured application logging."""
    log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("brandphantom")
    logger.setLevel(level)
    return logger

logger = setup_logging()
