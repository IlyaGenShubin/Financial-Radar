import logging
import sys
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "component": getattr(record, "component", "unknown"),
            "correlationId": getattr(record, "correlationId", None),
            "ruleId": getattr(record, "ruleId", None),
        }
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler])
