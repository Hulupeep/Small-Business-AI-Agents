"""
Centralized logging utility for business agents
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with both file and console handlers

    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level
        format_string: Custom format string

    Returns:
        Configured logger instance
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Default format
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    formatter = logging.Formatter(format_string)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def log_business_metric(logger: logging.Logger, metric_name: str, value: float, unit: str = ""):
    """Log business metrics in a structured format"""
    timestamp = datetime.now().isoformat()
    logger.info(f"METRIC | {timestamp} | {metric_name} | {value} {unit}")


def log_agent_action(logger: logging.Logger, action: str, details: dict):
    """Log agent actions with structured details"""
    timestamp = datetime.now().isoformat()
    details_str = " | ".join([f"{k}:{v}" for k, v in details.items()])
    logger.info(f"ACTION | {timestamp} | {action} | {details_str}")


def log_error_with_context(logger: logging.Logger, error: Exception, context: dict):
    """Log errors with additional context"""
    timestamp = datetime.now().isoformat()
    context_str = " | ".join([f"{k}:{v}" for k, v in context.items()])
    logger.error(f"ERROR | {timestamp} | {type(error).__name__}: {error} | {context_str}")