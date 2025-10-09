import logging
import sys
from logging.handlers import RotatingFileHandler

from pythonjsonlogger import jsonlogger


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    stdout_formatter = logging.Formatter(stdout_format, datefmt="%Y-%m-%d %H:%M:%S")
    stdout_handler.setFormatter(stdout_formatter)

    file_handler = RotatingFileHandler("app.log", maxBytes=10485760, backupCount=5)
    file_handler.setLevel(logging.INFO)
    json_format = "%(asctime)s %(name)s %(levelname)s %(lineno)d %(message)s"
    json_formatter = jsonlogger.JsonFormatter(json_format)
    file_handler.setFormatter(json_formatter)

    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)
