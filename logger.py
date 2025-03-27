import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class AppLogger:
    """Centralized logging system for the application"""
    
    def __init__(self, log_dir="logs", log_level=logging.INFO):
        """Initialize the logger with configurable log directory and level"""
        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Set up the logger
        self.logger = logging.getLogger("StructureManagementApp")
        self.logger.setLevel(log_level)
        self.logger.propagate = False  # Prevent duplicate logs
        
        # Clear any existing handlers (important for reinitialization)
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Create a formatter with timestamp, level, and message
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Create file handler with rotation (max 5MB per file, keep 5 backup files)
        log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5*1024*1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message):
        """Log a debug message"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log an info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log a warning message"""
        self.logger.warning(message)
    
    def error(self, message, exc_info=False):
        """Log an error message, optionally with exception info"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message, exc_info=True):
        """Log a critical message with exception info"""
        self.logger.critical(message, exc_info=exc_info)