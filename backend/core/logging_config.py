"""
Logging configuration for structured logging with rotation and environment-based levels.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from pythonjsonlogger import jsonlogger
import os


def setup_logging(environment: str = "development", log_level: str = None):
    """
    Configure application logging with rotation and structured output.
    
    Args:
        environment: 'development' or 'production'
        log_level: Override default log level (DEBUG, INFO, WARNING, ERROR)
    """
    # Determine log level
    if log_level:
        level = getattr(logging, log_level.upper())
    else:
        level = logging.DEBUG if environment == "development" else logging.INFO
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Console handler (always present)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=10_000_000,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    
    # Error file handler (only ERROR and above)
    error_handler = RotatingFileHandler(
        filename=log_dir / "error.log",
        maxBytes=5_000_000,  # 5 MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    
    # Formatters
    if environment == "production":
        # JSON formatter for production (easier to parse)
        json_formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s',
            rename_fields={"levelname": "level", "asctime": "timestamp"}
        )
        file_handler.setFormatter(json_formatter)
        error_handler.setFormatter(json_formatter)
        
        # Simple console format for production
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
    else:
        # Detailed format for development
        dev_formatter = logging.Formatter(
            '%(asctime)s - %(name)-30s - %(levelname)-8s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(dev_formatter)
        file_handler.setFormatter(dev_formatter)
        error_handler.setFormatter(dev_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Silence noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Log startup message
    environment_msg = f"Logging configured for {environment} environment at {level} level"
    root_logger.info(environment_msg)
    
    return root_logger


# Request ID context (for tracking requests across logs)
class RequestIDFilter(logging.Filter):
    """Add request ID to log records"""
    
    def __init__(self):
        super().__init__()
        self.request_id = None
    
    def filter(self, record):
        record.request_id = getattr(self, 'request_id', 'N/A')
        return True


# Get logger helper
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)
