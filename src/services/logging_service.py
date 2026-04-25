import logging
import sys
from logging.handlers import RotatingFileHandler


class FlushHandler(RotatingFileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()


def setup_logger(n="emerald_itr", f="emerald_itr.log", level=None):
    if level is None:
        try:
            from src.services.settings_service import SettingsManager

            level_str = SettingsManager.get("Engine.log_level", "INFO").upper()
            level = getattr(logging, level_str, logging.INFO)
        except Exception:
            level = logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = []
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    try:
        fh = FlushHandler(f, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
        fh.setFormatter(fmt)
        fh.setLevel(level)
        root_logger.addHandler(fh)
    except Exception as e:
        print(f"Failed to initialize file logging: {e}")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    ch.setLevel(level)
    root_logger.addHandler(ch)
    logger = logging.getLogger(n)
    logger.debug("Logging system initialized (Console + File)")
    return logger


log = logging.getLogger("emerald_itr")
