import os
import datetime as dt
from functools import lru_cache
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import traceback
from typing import Any
from uuid import UUID

from app.configs.utils import get_settings

FILENAME_LOGS = "logs/app.log"
if not os.path.exists(FILENAME_LOGS):
    os.makedirs(os.path.dirname(FILENAME_LOGS), exist_ok=True)
    with open(FILENAME_LOGS, "w", encoding="utf-8") as f:
        f.write("")


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> str:
        if isinstance(obj, dt.datetime):
            return obj.isoformat()
        return str(obj)


class LogFormatterJson(logging.Formatter):
    def format(self, record: Any) -> str:
        if not isinstance(record.msg, (str, dict)):
            record.msg = str(record.msg)
        log_record = {
            "time_generated": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "log_type": "struct" if isinstance(record.msg, dict) else "string",
            "log": record.msg,
        }
        return json.dumps(log_record, cls=CustomJSONEncoder)


class LogFormatterTerminal(logging.Formatter):
    def format(self, record: Any) -> str:
        if not isinstance(record.msg, (str, dict)):
            record.msg = str(record.msg)
        log_record = {
            "time_generated": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "log_type": "struct" if isinstance(record.msg, dict) else "string",
            "log": record.msg,
        }
        return json.dumps(log_record, cls=CustomJSONEncoder, indent=4)


@lru_cache()
def get_logger() -> logging.Logger:
    settings = get_settings()

    logger = logging.getLogger(settings.logger_name)
    logger.setLevel(settings.logger_level)

    # Console handler
    handler_stream = logging.StreamHandler()
    formatter_stream = LogFormatterTerminal()
    handler_stream.setFormatter(formatter_stream)
    handler_stream.setLevel(settings.logger_level)
    logger.addHandler(handler_stream)

    # File handler
    handler_file = TimedRotatingFileHandler(
        FILENAME_LOGS, when="M", interval=5, utc=True, encoding="utf-8"
    )
    formatter_file = LogFormatterJson()
    handler_file.setFormatter(formatter_file)
    logger.addHandler(handler_file)

    return logger


def log_error(logger: logging.Logger, req_id: UUID, exc: Exception) -> None:
    log = {
        "timestamp": dt.datetime.now(dt.UTC).isoformat(),
        "req_id": req_id,
        "type": "error",
        "error_type": exc.__class__.__name__,
        "message": str(exc),
        "traceback": traceback.format_exc().splitlines(),
    }
    logger.error(log)
