import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask


def configure_logging(app: Flask) -> None:
    if any(existing.name == "application_file_handler" for existing in app.logger.handlers):
        return

    log_path = Path(app.config["LOG_FILE"])
    log_path.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        log_path,
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    handler.setLevel(app.config["LOG_LEVEL"])
    handler.name = "application_file_handler"

    app.logger.setLevel(app.config["LOG_LEVEL"])
    app.logger.addHandler(handler)
