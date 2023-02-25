import logging
from logging import handlers
import os
from datetime import datetime

def setup_logging(base_path: str) -> None:
    if not os.path.exists(base_path + os.sep + "Logs"):
        os.mkdir(base_path + os.sep + "Logs")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename = base_path + os.sep + "Logs/p2mmbot.log", # Log location
        encoding = "utf-8", # Log encoding
        mode = "w", # Make sure when ever the bot starts it starts fresh with logs
        maxBytes = 32 * 1024 * 1024,  # 32 MiB will be the max size for log files
        backupCount = 5,  # Rotate through 5 files
    )
    formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# A log function to both log to the log and print to the console
def log(msg: str) -> None:
    """Logs a message to both the console and the logger

    Args:
        msg (str): Message to be sent.
    """
    now = datetime.now()
    print(f'[{now.strftime("%d/%m/%Y %H:%M:%S")}] {msg}')
    logging.info(msg)