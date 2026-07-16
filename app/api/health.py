from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import ServiceUnavailable

from app.extensions import db

blueprint = Blueprint(
    "health",
    __name__,
    url_prefix="/api",
    description="Service health checks",
)


@blueprint.route("/health")
class HealthResource(MethodView):
    @blueprint.response(200)
    def get(self):
        """Return the current service status."""
        try:
            db.session.execute(text("SELECT 1"))
        except SQLAlchemyError as error:
            db.session.rollback()
            raise ServiceUnavailable("Database is unavailable.") from error
        return {
            "status": "ok",
            "database": "available",
            "ai": "configured" if current_app.config["OPENAI_API_KEY"] else "fallback",
            "email": current_app.config["EMAIL_MODE"],
        }
