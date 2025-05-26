# Setting up a file and a console logging
# Author: derMax450

import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    # Check directories
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Rotating File Handler
    handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # do not use double handlers
    if not logger.hasHandlers():
        logger.addHandler(handler)

        # Optional: log to the console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger