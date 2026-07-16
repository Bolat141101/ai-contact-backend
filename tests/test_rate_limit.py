from app import create_app
from app.config import Config
from app.extensions import db


class RateLimitConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    OPENAI_API_KEY = None
    EMAIL_MODE = "console"
    SECRET_KEY = "rate-limit-test-secret"
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_HEADERS_ENABLED = True
    CONTACT_RATE_LIMIT = "2 per minute"


PAYLOAD = {
    "name": "Rate Limit User",
    "phone": "+77001234567",
    "email": "rate@example.com",
    "comment": "This message is long enough for validation.",
}


def test_contact_rate_limit_returns_429():
    app = create_app(RateLimitConfig)
    with app.app_context():
        db.create_all()
        client = app.test_client()

        assert client.post("/api/contact", json=PAYLOAD).status_code == 201
        assert client.post("/api/contact", json=PAYLOAD).status_code == 201
        response = client.post("/api/contact", json=PAYLOAD)

        assert response.status_code == 429
        assert response.get_json()["error"]["code"] == "TOO_MANY_REQUESTS"
        assert response.headers["Retry-After"]

        db.session.remove()
        db.drop_all()
