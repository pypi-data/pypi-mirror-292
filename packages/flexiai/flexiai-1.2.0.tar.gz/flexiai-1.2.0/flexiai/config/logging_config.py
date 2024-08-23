# flexiai/config/logging_config.py
import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(root_level=logging.INFO, file_level=logging.INFO, console_level=logging.INFO, enable_file_logging=True, enable_console_logging=True):
    """
    Configures the logging settings for the application with user-defined log levels.

    Parameters:
    - root_level: Logging level for the root logger.
    - file_level: Logging level for the file handler.
    - console_level: Logging level for the console handler.
    - enable_file_logging: Boolean flag to enable or disable file logging.
    - enable_console_logging: Boolean flag to enable or disable console logging.

    This function sets up a logger with the following features:
    - Logs messages at the specified levels and above.
    - Uses a rotating file handler to manage log file sizes and backups.
    - Formats log messages with a specific format.
    - Ensures that log messages are also output to the console for real-time monitoring.

    Logging Details:
    - Log file path: 'logs/app.log'
    - Maximum log file size: 5 MB
    - Number of backup log files to keep: 3
    - Log message format: '%(asctime)s - %(levelname)s - %(filename)s - %(message)s'

    The rotating file handler helps in managing disk space by rotating the log file 
    once it reaches a specified size, and keeping a defined number of backup files.

    The console handler ensures that log messages are visible in the console in real-time,
    which is useful for debugging during development and monitoring in production.

    This setup prevents multiple handlers from being added if the function is called 
    more than once.
    """
    
    # Print current working directory to ensure we are in the correct location
    current_directory = os.getcwd()
    print(f"Current working directory: {current_directory}")

    # Define log directory and file relative to the project root
    log_directory = os.path.join(current_directory, "logs")
    log_file = os.path.join(log_directory, "app.log")

    # Ensure the log directory exists
    try:
        os.makedirs(log_directory, exist_ok=True)
        print(f"Log directory '{log_directory}' created/exists.")
    except OSError as e:
        print(f"Error creating log directory {log_directory}: {e}")
        return
    
    # Get the root logger instance
    logger = logging.getLogger()
    
    # Clear existing handlers to prevent duplication
    if logger.hasHandlers():
        logger.handlers.clear()

    try:
        # Set the logging level for the root logger
        logger.setLevel(root_level)

        if enable_file_logging:
            # Create a rotating file handler to manage log files
            file_handler = RotatingFileHandler(
                log_file,                      # Path to the log file
                maxBytes=5 * 1024 * 1024,      # Maximum file size: 5 MB
                backupCount=3                  # Number of backup files to keep
            )
            
            # Set the file handler's logging level
            file_handler.setLevel(file_level)

            # Create a formatter to define the log message format
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(filename)s - %(message)s"  # Log message format with date
            )
            
            # Assign the formatter to the file handler
            file_handler.setFormatter(formatter)

            # Add the file handler to the logger
            logger.addHandler(file_handler)

        if enable_console_logging:
            # Create a console handler to output log messages to the console
            console_handler = logging.StreamHandler()
            
            # Set the console handler's logging level
            console_handler.setLevel(console_level)
            
            # Assign the formatter to the console handler
            console_handler.setFormatter(formatter)
            
            # Add the console handler to the logger
            logger.addHandler(console_handler)
    except Exception as e:
        print(f"Error setting up logging: {e}")
