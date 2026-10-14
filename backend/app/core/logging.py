"""JSON logging for application-owned events."""

import json
import logging
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        item = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            item["exception"] = self.formatException(record.exc_info)
        return json.dumps(item, ensure_ascii=False)


def configure_logging() -> None:
    logger = logging.getLogger("teachflow")
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
