"""Enhanced logging for SimpleDL.

Provides structured logging with context, timing, and detailed error information.
"""
import logging
import logging.handlers
import sys
import time
from pathlib import Path
from typing import Optional
from datetime import datetime


class TimedFormatter(logging.Formatter):
    """Formatter that includes timestamps and context."""
    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "start_time"):
            record.start_time = datetime.now()
        return super().format(record)


class ContextFilter(logging.Filter):
    """Filter that adds context info to log records."""
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "context"):
            record.context = ""
        return True


def setup_logging(log_path: Optional[str] = None, verbosity: str = "info") -> logging.Logger:
    """Set up enhanced logging for SimpleDL.
    
    Args:
        log_path: Path to log file (default: ./logs/downloads.log)
        verbosity: Log level (info, debug)
    
    Returns:
        Configured logger instance
    """
    if not log_path:
        log_path = "./logs/downloads.log"
    
    log_file = Path(log_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("simpledl")
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Set log level
    level = logging.DEBUG if verbosity.lower() == "debug" else logging.INFO
    logger.setLevel(level)
    
    # Add context filter
    logger.addFilter(ContextFilter())
    
    # Format string
    fmt_str = "%(asctime)s [%(levelname)s] %(message)s"
    if verbosity.lower() == "debug":
        fmt_str = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
    
    formatter = TimedFormatter(fmt_str, datefmt="%Y-%m-%d %H:%M:%S")
    
    # File handler (verbose)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # Always log debug to file
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler (user-friendly)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter("%(message)s")  # Simple format for console
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


def log_download_context(
    logger: logging.Logger,
    url: str,
    download_type: str,
    fmt: str,
    quality: str,
    out_dir: str
):
    """Log download context at start."""
    logger.info(f"=== Download Start ===")
    logger.info(f"URL: {url}")
    logger.info(f"Type: {download_type}")
    logger.info(f"Format: {fmt}, Quality: {quality}")
    logger.info(f"Output: {out_dir}")


def log_download_result(
    logger: logging.Logger,
    success: bool,
    duration: float,
    filename: Optional[str] = None,
    error: Optional[str] = None
):
    """Log download result at end."""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Result: {status}")
    if filename:
        logger.info(f"Filename: {filename}")
    if error:
        logger.error(f"Error: {error}")
    logger.info(f"Duration: {duration:.2f}s")
    logger.info(f"=== Download End ===")
    logger.info("")  # blank line for readability
