import logging
import sys
import json
import datetime
from typing import Any, Dict, Optional

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if hasattr(record, "props") and isinstance(record.props, dict):
            log_obj.update(record.props)
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

class MantaLogger(logging.Logger):
    def with_fields(self, **kwargs: Any) -> "StructuredLoggerAdapter":
        return StructuredLoggerAdapter(self, kwargs)

class StructuredLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg: str, kwargs: Any) -> tuple[str, Any]:
        props = self.extra.copy() if self.extra else {}
        if "extra" in kwargs:
            props.update(kwargs.pop("extra"))
        kwargs["extra"] = {"props": props}
        return msg, kwargs

def setup_logging(level: str = "INFO", json_format: bool = False) -> None:
    root = logging.getLogger("manta")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        fmt = "%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s"
        handler.setFormatter(logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S"))
    
    root.addHandler(handler)

def get_logger(name: str = "manta") -> logging.Logger:
    return logging.getLogger(f"manta.{name}")
