import re
import time
from uuid import uuid4

from flask import Flask, g, request

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def configure_request_context(app: Flask) -> None:
    @app.before_request
    def start_request():
        supplied_request_id = request.headers.get("X-Request-ID", "")
        g.request_id = (
            supplied_request_id
            if REQUEST_ID_PATTERN.fullmatch(supplied_request_id)
            else str(uuid4())
        )
        g.request_started_at = time.monotonic()

    @app.after_request
    def finish_request(response):
        duration_ms = round((time.monotonic() - g.request_started_at) * 1000, 2)
        response.headers["X-Request-ID"] = g.request_id
        app.logger.info(
            "request_completed request_id=%s method=%s path=%s status=%s duration_ms=%s",
            g.request_id,
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response
