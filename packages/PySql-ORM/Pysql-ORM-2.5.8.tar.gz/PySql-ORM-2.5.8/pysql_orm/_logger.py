import logging
import os

logger_name = os.environ.get("SQLALCHEMY_LOGGER", "flask.app")
logger = logging.getLogger(logger_name)
