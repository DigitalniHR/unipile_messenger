"""
Logging utilities for UniPile Messenger.
Provides timestamped logging to both console and file.
"""
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config


def setup_logging(name: str = "unipile") -> logging.Logger:
    """
    Set up logging with both console and file handlers.

    Args:
        name: Logger name (default: "unipile")

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, Config.LOG_LEVEL, logging.INFO))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (if logs directory exists)
    Config.LOGS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Config.LOGS_DIR / f"{timestamp}_{name}.log"

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "unipile") -> logging.Logger:
    """Get existing logger or create new one."""
    return logging.getLogger(name)
