from functools import lru_cache
import logging
from logging.handlers import TimedRotatingFileHandler
import json
import datetime as dt
from uuid import UUID

from app.utils.configs import get_settings
from app.constants.constants import FILENAME_LOGS


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, dt.datetime):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return obj.hex
        return super().default(obj)


class LogFormatterJson(logging.Formatter):
    def format(self, record):
        if not isinstance(record.msg, (str, dict)):
            record.msg = str(record.msg)
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "log_type": "struct" if isinstance(record.msg, dict) else "string",
            "log": record.msg,
        }
        return json.dumps(log_record, cls=CustomJSONEncoder)


@lru_cache()
def get_logger() -> logging.Logger:
    settings = get_settings()

    logger = logging.getLogger(settings.logger_name)
    logger.setLevel(settings.logger_level)

    handler_file = TimedRotatingFileHandler(
        FILENAME_LOGS, when="M", interval=5, utc=True, encoding="utf-8"
    )
    formatter_file = LogFormatterJson(
        fmt='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "log": %(message)s}',
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler_file.setFormatter(formatter_file)
    logger.addHandler(handler_file)

    return logger
