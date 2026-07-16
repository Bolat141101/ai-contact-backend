from app.models.contact import Contact
from app.services.email_service import EmailService


class FakeSMTP:
    instances = []

    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.tls_started = False
        self.credentials = None
        self.messages = []
        self.__class__.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def starttls(self):
        self.tls_started = True

    def login(self, username, password):
        self.credentials = (username, password)

    def send_message(self, message):
        self.messages.append(message)


def test_email_service_sends_owner_and_customer_emails(app, monkeypatch):
    FakeSMTP.instances.clear()
    monkeypatch.setattr("app.services.email_service.smtplib.SMTP", FakeSMTP)

    with app.app_context():
        app.config.update(
            EMAIL_MODE="smtp",
            SMTP_HOST="smtp.example.com",
            SMTP_PORT=587,
            SMTP_USERNAME="mailer",
            SMTP_PASSWORD="secret",
            SMTP_USE_TLS=True,
            EMAIL_FROM="site@example.com",
            OWNER_EMAIL="owner@example.com",
        )
        contact = Contact(
            id=42,
            name="Иван Петров",
            phone="+7 777 123-45-67",
            email="ivan@example.com",
            comment="Нужен интернет-магазин",
            category="development",
            sentiment="positive",
            priority="normal",
            ai_reply="Спасибо! Свяжемся с вами.",
        )

        statuses = EmailService().send_contact_emails(contact)

    assert statuses == ("sent", "sent")
    assert len(FakeSMTP.instances) == 2
    messages = [instance.messages[0] for instance in FakeSMTP.instances]
    assert [message["To"] for message in messages] == [
        "owner@example.com",
        "ivan@example.com",
    ]
    assert all(message["From"] == "site@example.com" for message in messages)
    assert all(instance.tls_started for instance in FakeSMTP.instances)
    assert all(instance.credentials == ("mailer", "secret") for instance in FakeSMTP.instances)
    assert "Новое обращение #42" in messages[0]["Subject"]
    customer_html = messages[1].get_body(preferencelist=("html",)).get_content()
    assert "Спасибо! Свяжемся с вами." in customer_html


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
