from app.services.email_service import EmailService


def test_email_service_returns_failed_on_smtp_error(app, monkeypatch):
    def fail_delivery(*args, **kwargs):
        raise TimeoutError("smtp timed out")

    monkeypatch.setattr(EmailService, "_send_smtp", fail_delivery)

    with app.app_context():
        app.config["EMAIL_MODE"] = "smtp"
        app.config["SMTP_HOST"] = "smtp.example.com"
        status = EmailService()._deliver(
            "customer",
            "user@example.com",
            "Test subject",
            "<p>Test body</p>",
        )

    assert status == "failed"
