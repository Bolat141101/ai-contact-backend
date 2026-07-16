from app.extensions import db
from app.models.contact import Contact


def test_metrics_require_api_key(client):
    response = client.get("/api/metrics")

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "UNAUTHORIZED"


def test_metrics_return_aggregates_without_personal_data(client, app):
    with app.app_context():
        db.session.add(
            Contact(
                name="Test User",
                phone="+77001234567",
                email="test@example.com",
                comment="A sufficiently long test message",
                category="project_request",
                ai_processed=False,
                owner_email_status="failed",
                customer_email_status="sent",
            )
        )
        db.session.commit()

    response = client.get(
        "/api/metrics",
        headers={"X-API-Key": "test-metrics-key"},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "total": 1,
        "last_24_hours": 1,
        "ai_fallbacks": 1,
        "email_failures": 1,
        "by_category": {"project_request": 1},
    }
