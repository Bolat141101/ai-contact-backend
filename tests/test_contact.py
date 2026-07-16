from app.extensions import db
from app.models.contact import Contact

VALID_CONTACT = {
    "name": "Иван Петров",
    "phone": "+7 (777) 123-45-67",
    "email": "ivan@example.com",
    "comment": "Хочу обсудить разработку небольшого веб-сервиса.",
}


def test_create_contact_with_ai_fallback(client, app):
    response = client.post("/api/contact", json=VALID_CONTACT)

    assert response.status_code == 201
    assert response.get_json() == {
        "id": 1,
        "status": "accepted",
        "message": "Обращение принято",
        "ai_processed": False,
        "ai": {
            "category": "other",
            "sentiment": "neutral",
            "priority": "normal",
            "reply": (
                "Спасибо за обращение. Я получил ваше сообщение и свяжусь с вами в ближайшее время."
            ),
        },
    }
    assert response.headers["X-Request-ID"]

    with app.app_context():
        contact = db.session.get(Contact, 1)
        assert contact is not None
        assert contact.ai_status == "disabled"
        assert contact.owner_email_status == "logged"
        assert contact.customer_email_status == "logged"
        assert contact.ip_hash != "127.0.0.1"


def test_rejects_invalid_fields(client):
    response = client.post(
        "/api/contact",
        json={
            "name": "A",
            "phone": "123",
            "email": "not-an-email",
            "comment": "short",
        },
    )

    assert response.status_code == 422
    payload = response.get_json()
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["request_id"]
    assert "json" in payload["error"]["details"]


def test_rejects_unknown_fields(client):
    response = client.post(
        "/api/contact",
        json={**VALID_CONTACT, "is_admin": True},
    )

    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


def test_rejects_non_json_request(client):
    response = client.post(
        "/api/contact",
        data="name=Ivan",
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 422
