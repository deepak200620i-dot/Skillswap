"""
Logging utility for the SkillSwap application.
Provides centralized logging configuration and helpers.
"""

import logging
import logging.handlers
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Configure logger
logger = logging.getLogger("skillswap")
logger.setLevel(logging.INFO)

# File handler - logs to file
log_filename = os.path.join(
    LOGS_DIR, f'skillswap_{datetime.now().strftime("%Y%m%d")}.log'
)
file_handler = logging.handlers.RotatingFileHandler(
    log_filename, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
)
file_handler.setLevel(logging.DEBUG)

# Console handler - logs to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def log_info(message, extra_data=None):
    """Log info level message"""
    if extra_data:
        logger.info(f"{message} | Extra: {extra_data}")
    else:
        logger.info(message)


def log_warning(message, extra_data=None):
    """Log warning level message"""
    if extra_data:
        logger.warning(f"{message} | Extra: {extra_data}")
    else:
        logger.warning(message)


def log_error(message, extra_data=None, exception=None):
    """Log error level message"""
    if extra_data:
        message = f"{message} | Extra: {extra_data}"

    if exception:
        logger.error(message, exc_info=exception)
    else:
        logger.error(message)


def log_debug(message, extra_data=None):
    """Log debug level message"""
    if extra_data:
        logger.debug(f"{message} | Extra: {extra_data}")
    else:
        logger.debug(message)


def log_request(method, path, user_id=None, status_code=None):
    """Log API request"""
    user_info = f"user_id={user_id}" if user_id else "anonymous"
    status_info = f"status={status_code}" if status_code else "pending"
    logger.info(f"API Request: {method} {path} | {user_info} | {status_info}")


def log_database_error(operation, table, error):
    """Log database error with context"""
    logger.error(f"Database Error: {operation} on {table} | Error: {error}")


def log_security_event(event_type, user_id=None, details=None):
    """Log security-related events"""
    user_info = f"user_id={user_id}" if user_id else "unknown_user"
    details_info = f" | {details}" if details else ""
    logger.warning(f"Security Event: {event_type} | {user_info}{details_info}")
