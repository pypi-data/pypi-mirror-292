import logging
import logging.handlers
import sys
import os

# Determine the log file directory
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')

# Create the log directory if it doesn't exist
os.makedirs(log_dir, exist_ok=True)

# Create a custom filter to only allow INFO level logs to the console
class InfoFilter(logging.Filter):
    """Filter to allow only INFO level logs."""
    def filter(self, record):
        return record.levelno == logging.INFO

# Logging configuration
def get_logger(module_name):
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)  # Set the root logger level to DEBUG

    formatter = logging.Formatter('%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

    # Console handler for logging to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Set console to capture INFO and above
    console_handler.setFormatter(formatter)

    # Apply the InfoFilter to only show INFO level logs in the console
    console_handler.addFilter(InfoFilter())

    # File handler for logging to a file with DEBUG level
    log_file = os.path.join(log_dir, 'app.log')  # Customize log file name and path
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1024 * 1024 * 5, backupCount=5  # 5 MB log file with 5 rotations
    )
    file_handler.setLevel(logging.DEBUG)  # Log DEBUG and above to file
    file_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
