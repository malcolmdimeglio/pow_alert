#! /usr/bin/env python
import os
import logging, logging.handlers

curr_dir = os.path.dirname(os.path.realpath(__file__))
logFile = f"{curr_dir}/log/pow_alert.log"

class CustomFormatter(logging.Formatter):
    """Logging Formatter to different format style depending on log levels"""

    FORMATS = {
        "CRITICAL": "%(asctime)s - %(levelname)s: %(module)s: %(msg)s",
        "ERROR":    "%(asctime)s - %(levelname)s: %(module)s[%(lineno)d]: %(msg)s",
        "WARNING":  "%(asctime)s - %(levelname)s: %(module)s: %(msg)s",
        "INFO":     "%(asctime)s - %(levelname)s: %(module)s: %(msg)s",
        "DEBUG":    "%(asctime)s - %(levelname)s: %(module)s[%(lineno)d]: %(msg)s",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEBUG'])
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

log_handler = logging.handlers.RotatingFileHandler(logFile, maxBytes=(10 * 1024 * 1024), backupCount=5)
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(CustomFormatter())
log.addHandler(log_handler)


# Format reminder:
# %(levelname)s: Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
# %(lineno)d: Source line number where the logging call was issued (if available).
# %(message)s: The logged messaged
# %(module)s: Module (name portion of filename)
# %(asctime)s: Time at which the logger has been called.
