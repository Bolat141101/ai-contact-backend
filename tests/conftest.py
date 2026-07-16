import pytest

from app import create_app
from app.config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    OPENAI_API_KEY = None
    EMAIL_MODE = "console"
    RATELIMIT_ENABLED = False
    SECRET_KEY = "test-secret"
    METRICS_API_KEY = "test-metrics-key"


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    from app.extensions import db

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
