import secrets
from functools import wraps

from flask import current_app, request
from flask.views import MethodView
from flask_smorest import Blueprint
from werkzeug.exceptions import ServiceUnavailable, Unauthorized

from app.schemas.metrics import MetricsResponseSchema
from app.services.metrics_service import MetricsService

blueprint = Blueprint(
    "metrics",
    __name__,
    url_prefix="/api",
    description="Contact request statistics",
)


def require_metrics_api_key(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        expected = current_app.config["METRICS_API_KEY"]
        if not expected:
            raise ServiceUnavailable("Metrics endpoint is not configured.")
        provided = request.headers.get("X-API-Key", "")
        if not secrets.compare_digest(provided, expected):
            raise Unauthorized("Invalid metrics API key.")
        return view(*args, **kwargs)

    return wrapped


@blueprint.route("/metrics")
class MetricsResource(MethodView):
    @blueprint.response(200, MetricsResponseSchema)
    @require_metrics_api_key
    def get(self):
        """Return aggregate contact statistics without personal data."""
        return MetricsService().get_summary()
