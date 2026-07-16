from app.extensions import db
from app.models.contact import Contact


class ContactRepository:
    def create(self, **values) -> Contact:
        contact = Contact(**values)
        db.session.add(contact)
        db.session.commit()
        return contact

    def save(self, contact: Contact) -> Contact:
        db.session.commit()
        return contact
