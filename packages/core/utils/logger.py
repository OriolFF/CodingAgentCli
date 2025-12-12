"""Structured logging system with model/provider context.

This module provides a configured logger that includes information about
the model and provider being used, helpful for debugging multi-provider issues.
"""

import logging
import sys
from typing import Optional


# ANSI color codes for terminal output
COLORS = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[35m",  # Magenta
    "RESET": "\033[0m",  # Reset
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels in terminal output."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log string with ANSI colors
        """
        # Add color to level name
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
        
        return super().format(record)


def configure_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    use_colors: bool = True,
) -> None:
    """Configure the logging system.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string. If None, uses default.
        use_colors: Whether to use colored output in terminal
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create formatter
    if use_colors and sys.stdout.isatty():
        formatter = ColoredFormatter(format_string)
    else:
        formatter = logging.Formatter(format_string)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Context-aware logger helper
class ModelLogger:
    """Logger wrapper that adds model/provider context to log messages."""
    
    def __init__(self, logger: logging.Logger, model_name: str, provider: str):
        """Initialize model logger.
        
        Args:
            logger: Base logger instance
            model_name: Name of the model
            provider: Provider name
        """
        self.logger = logger
        self.model_name = model_name
        self.provider = provider
        self.prefix = f"[{provider}:{model_name}]"
    
    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log debug message with model context."""
        self.logger.debug(f"{self.prefix} {msg}", *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs) -> None:
        """Log info message with model context."""
        self.logger.info(f"{self.prefix} {msg}", *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log warning message with model context."""
        self.logger.warning(f"{self.prefix} {msg}", *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs) -> None:
        """Log error message with model context."""
        self.logger.error(f"{self.prefix} {msg}", *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log critical message with model context."""
        self.logger.critical(f"{self.prefix} {msg}", *args, **kwargs)


def get_model_logger(name: str, model_name: str, provider: str) -> ModelLogger:
    """Get a model-aware logger.
    
    Args:
        name: Logger name  
        model_name: Name of the model
        provider: Provider name
        
    Returns:
        ModelLogger instance with context
    """
    base_logger = get_logger(name)
    return ModelLogger(base_logger, model_name, provider)
