import logging
import os

__all__ = ["get_default_logger", "LOG"]


def get_default_logger(name):
    # https://stackoverflow.com/questions/43109355/logging-setlevel-is-being-ignored
    logging.debug(f"Setting up logging for logger={name}")
    logger = logging.getLogger(name)
    logger.setLevel(level=os.environ.get("LOG_LEVEL", "INFO"))
    return logger


LOG = get_default_logger("hl_client")
