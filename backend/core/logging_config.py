import logging
import json
from google.cloud import logging as cloud_logging


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.name,
        }

        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data)


def setup_logging():
    try:
        client = cloud_logging.Client()
        client.setup_logging()
        return True
    except Exception:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)
        return False


logger = logging.getLogger("monte_carlo")


def log_info(message: str, **extra):
    if extra:
        record = logger.makeRecord(logger.name, logging.INFO, "", 0, message, (), None)
        record.extra = extra
        logger.handle(record)
    else:
        logger.info(message)


def log_error(message: str, **extra):
    if extra:
        record = logger.makeRecord(logger.name, logging.ERROR, "", 0, message, (), None)
        record.extra = extra
        logger.handle(record)
    else:
        logger.error(message)
