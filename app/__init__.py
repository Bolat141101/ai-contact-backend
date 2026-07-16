from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from app.api.contact import blueprint as contact_blueprint
from app.api.health import blueprint as health_blueprint
from app.api.metrics import blueprint as metrics_blueprint
from app.config import Config
from app.errors.handlers import register_error_handlers
from app.extensions import api, cors, db, limiter, migrate
from app.logging_config import configure_logging
from app.middleware.request_context import configure_request_context
from app.web import blueprint as web_blueprint


def create_app(config_object: type[Config] = Config) -> Flask:
    """Application factory used by local, production, and test environments."""
    app = Flask(__name__)
    app.config.from_object(config_object)

    if app.config["TRUST_PROXY_HOPS"]:
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=app.config["TRUST_PROXY_HOPS"],
            x_proto=app.config["TRUST_PROXY_HOPS"],
        )

    configure_logging(app)
    configure_request_context(app)

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Request-ID", "X-API-Key"],
    )
    api.init_app(app)
    api.register_blueprint(health_blueprint)
    api.register_blueprint(contact_blueprint)
    api.register_blueprint(metrics_blueprint)
    app.register_blueprint(web_blueprint)
    register_error_handlers(app)

    return app
