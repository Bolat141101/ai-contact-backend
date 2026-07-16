import hashlib

from flask import current_app

from app.repositories.contact_repository import ContactRepository
from app.services.ai_service import AIService
from app.services.email_service import EmailService


class ContactService:
    def __init__(
        self,
        repository: ContactRepository | None = None,
        ai_service: AIService | None = None,
        email_service: EmailService | None = None,
    ):
        self.repository = repository or ContactRepository()
        self.ai_service = ai_service or AIService()
        self.email_service = email_service or EmailService()

    def create_contact(self, data: dict, remote_address: str | None) -> dict:
        contact = self.repository.create(
            **data,
            ip_hash=self._hash_ip(remote_address),
        )

        analysis = self.ai_service.analyze(contact.comment)
        contact.category = analysis.category
        contact.sentiment = analysis.sentiment
        contact.priority = analysis.priority
        contact.ai_reply = analysis.reply_draft
        contact.ai_processed = analysis.processed
        contact.ai_status = analysis.status
        self.repository.save(contact)

        owner_status, customer_status = self.email_service.send_contact_emails(contact)
        contact.owner_email_status = owner_status
        contact.customer_email_status = customer_status
        self.repository.save(contact)

        return {
            "id": contact.id,
            "status": "accepted",
            "message": "Обращение принято",
            "ai_processed": contact.ai_processed,
            "ai": {
                "category": contact.category,
                "sentiment": contact.sentiment,
                "priority": contact.priority,
                "reply": contact.ai_reply,
            },
        }

    @staticmethod
    def _hash_ip(remote_address: str | None) -> str | None:
        if not remote_address:
            return None
        value = f"{current_app.config['SECRET_KEY']}:{remote_address}".encode()
        return hashlib.sha256(value).hexdigest()
