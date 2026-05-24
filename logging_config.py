import logging
import sys
from pathlib import Path
from datetime import datetime

class SwitchCLIFormatter(logging.Formatter):
    """Format logs as Switch CLI syslog messages."""
    
    LEVEL_MAP = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARN",
        logging.ERROR: "ERR",
        logging.CRITICAL: "CRIT"
    }
    
    def format(self, record):
        level_str = self.LEVEL_MAP.get(record.levelno, "LOG")
        # Format as: @ YYYY-MM-DD HH:MM:SS - [MODULE:LEVEL] - MESSAGE
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        module = record.name if record.name != "root" else "FENR1R"
        return f"@ {timestamp} - [{module}:{level_str}] - {record.getMessage()}"

def setup_logging(log_file="fenr1r.log", level=logging.INFO):
    """Setup logging to file and console with Switch CLI formatting."""
    # Get root logger
    root_logger = logging.getLogger()
    
    # Prevent duplicate handlers
    if root_logger.hasHandlers():
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    root_logger.setLevel(level)
    root_logger.propagate = False

    # Use custom Switch CLI formatter
    formatter = SwitchCLIFormatter()

    # File handler
    log_path = Path(log_file)
    try:
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to setup file handler: {e}")

    # Console handler with same formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Suppress warnings from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("transformers").setLevel(logging.ERROR)

    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Get a named logger to avoid root logger issues."""
    return logging.getLogger(name)