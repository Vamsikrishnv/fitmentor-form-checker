# backend/logging_config.py
"""
Centralized logging configuration for FitMentor AI backend.
"""
import logging
import sys
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    """
    Configure application-wide logging.

    Sets up console and file handlers with appropriate formatting.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Remove existing handlers
    logger.handlers = []

    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Formatters
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)

    logger.addHandler(console_handler)

    # Optionally add file handler for production
    if os.getenv("ENABLE_FILE_LOGGING", "false").lower() == "true":
        try:
            file_handler = RotatingFileHandler(
                'logs/fitmentor.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.INFO)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not set up file logging: {e}")

    # Suppress overly verbose third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("mediapipe").setLevel(logging.WARNING)

    return logger


# Create default logger
logger = setup_logging()
