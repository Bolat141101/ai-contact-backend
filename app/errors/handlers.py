from flask import Flask, g
from werkzeug.exceptions import HTTPException

from app.extensions import db


def _error_payload(code: str, message: str, details=None):
    payload = {
        "error": {
            "code": code,
            "message": message,
            "request_id": getattr(g, "request_id", None),
        }
    }
    if details:
        payload["error"]["details"] = details
    return payload


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        data = getattr(error, "data", {}) or {}
        details = data.get("messages")
        code = "VALIDATION_ERROR" if error.code == 422 else error.name.upper().replace(" ", "_")
        message = "Request validation failed" if error.code == 422 else error.description
        return _error_payload(code, message, details), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        db.session.rollback()
        app.logger.exception(
            "unhandled_exception request_id=%s",
            getattr(g, "request_id", None),
        )
        return _error_payload("INTERNAL_ERROR", "Internal server error"), 500
