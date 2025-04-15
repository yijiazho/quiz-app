import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

def setup_logging(level=logging.INFO):
    """
    Set up logging configuration for the application
    
    Args:
        level: The logging level to use (default: INFO)
    """
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)
    
    # Create file handlers
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # General log file
    general_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / f'app_{current_date}.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    general_handler.setFormatter(file_formatter)
    general_handler.setLevel(level)
    
    # Error log file
    error_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / f'error_{current_date}.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setFormatter(file_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(general_handler)
    root_logger.addHandler(error_handler)
    
    # Set specific levels for some loggers
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)

# Environment-specific configuration
def configure_logging():
    """Configure logging based on environment"""
    env = os.getenv('ENVIRONMENT', 'development').lower()
    
    if env == 'production':
        setup_logging(level=logging.WARNING)
    elif env == 'testing':
        setup_logging(level=logging.DEBUG)
    else:  # development
        setup_logging(level=logging.INFO) 