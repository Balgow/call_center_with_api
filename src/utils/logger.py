import logging
import time
from functools import wraps
from datetime import datetime
from pathlib import Path
from typing import Callable, Any

# Create logs directory
BASE_DIR = Path(__file__).parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
def setup_logger(name: str) -> logging.Logger:
    """Setup and return a logger with the specified name"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(
        LOGS_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    # Create formatters
    log_format = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
    
    # Set formatters
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Create timing decorator
def timing_decorator(logger: logging.Logger) -> Callable:
    """Decorator to measure and log execution time of functions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Only log timing for GPT response
            if func.__name__ == 'process_speech_text':
                logger.info(f"Timing: {func.__name__} in {execution_time:.2f} seconds")
            
            return result
        return wrapper
    return decorator

default_logger = setup_logger('v1') 