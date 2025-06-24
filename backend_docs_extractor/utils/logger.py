# fmt: off
# isort: skip_file

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Logging configuration for the backend documentation generator

This module configures logging for the documentation generator,
with appropriate log levels, formats, and handlers.

Author: nanthiniSanthanam
Generated: 2025-05-04 05:13:56
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logger(verbosity: int = 1) -> logging.Logger:
    """Set up logging configuration

    Args:
        verbosity: Log verbosity level (0=quiet, 1=normal, 2=verbose, 3=debug)

    Returns:
        logging.Logger: Configured logger instance
    """
    # Map verbosity level to logging level
    log_levels = {
        0: logging.ERROR,
        1: logging.INFO,
        2: logging.INFO,  # Also INFO but more verbose output
        3: logging.DEBUG,
    }

    # Get log level
    log_level = log_levels.get(verbosity, logging.INFO)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Create formatter
    if verbosity >= 2:
        # More verbose format for higher verbosity levels
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        # Simpler format for normal operation
        formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )

    # Add formatter to handler
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Create file handler if verbosity is high
    if verbosity >= 2:
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        # Create log file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"backend_docs_{timestamp}.log"

        # Add file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always debug level for file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Return configured logger
    return logger