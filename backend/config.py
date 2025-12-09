import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv
import sys
import io

load_dotenv()

LOG_DIR = os.getenv("LOG_DIR")
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging():
    # Root Logger
    logger = logging.getLogger()
    # avoid adding duplicate handlers if `setup_logging` called multiple times
    if logger.handlers:
        return
    logger.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] — %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    # ----------- File: app.log (general logs) -----------
    file_handler = RotatingFileHandler(
        f"{LOG_DIR}/app.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # ----------- File: error.log -----------
    error_handler = RotatingFileHandler(
        f"{LOG_DIR}/error.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    
    # Wrap the standard error stream with a UTF-8 TextIOWrapper so
    # writing Unicode (e.g. emojis) doesn't raise encoding errors.
    try:
        stream = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        # Fallback: use the original stderr if wrapping isn't possible
        stream = sys.stderr

    console_handler = logging.StreamHandler(stream)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logging.info("Logging initialized.")
