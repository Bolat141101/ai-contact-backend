import smtplib
from email.message import EmailMessage

from flask import current_app, render_template

from app.models.contact import Contact


class EmailService:
    def send_contact_emails(self, contact: Contact) -> tuple[str, str]:
        owner_status = self._deliver(
            delivery_type="owner",
            recipient=current_app.config["OWNER_EMAIL"],
            subject=f"Новое обращение #{contact.id}",
            html=render_template("emails/owner.html", contact=contact),
        )
        customer_status = self._deliver(
            delivery_type="customer",
            recipient=contact.email,
            subject="Мы получили ваше обращение",
            html=render_template("emails/customer.html", contact=contact),
        )
        return owner_status, customer_status

    def _deliver(self, delivery_type: str, recipient: str, subject: str, html: str) -> str:
        mode = current_app.config["EMAIL_MODE"]
        if mode == "console":
            current_app.logger.info(
                "email_preview delivery_type=%s subject=%s body_length=%s",
                delivery_type,
                subject,
                len(html),
            )
            return "logged"

        if mode != "smtp":
            current_app.logger.warning("email_disabled invalid_mode=%s", mode)
            return "disabled"

        try:
            self._send_smtp(recipient, subject, html)
            return "sent"
        except Exception:
            current_app.logger.exception("email_delivery_failed delivery_type=%s", delivery_type)
            return "failed"

    @staticmethod
    def _send_smtp(recipient: str, subject: str, html: str) -> None:
        config = current_app.config
        if not config["SMTP_HOST"]:
            raise RuntimeError("SMTP_HOST is required when EMAIL_MODE=smtp")

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = config["EMAIL_FROM"]
        message["To"] = recipient
        message.set_content("This message requires an HTML-capable email client.")
        message.add_alternative(html, subtype="html")

        with smtplib.SMTP(config["SMTP_HOST"], config["SMTP_PORT"], timeout=10) as smtp:
            if config["SMTP_USE_TLS"]:
                smtp.starttls()
            if config["SMTP_USERNAME"]:
                smtp.login(config["SMTP_USERNAME"], config["SMTP_PASSWORD"] or "")
            smtp.send_message(message)
