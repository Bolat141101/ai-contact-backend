from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class Contact(db.Model):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    ip_hash: Mapped[str | None] = mapped_column(String(64))

    category: Mapped[str] = mapped_column(String(32), default="unknown")
    sentiment: Mapped[str] = mapped_column(String(16), default="neutral")
    priority: Mapped[str] = mapped_column(String(16), default="normal")
    ai_reply: Mapped[str | None] = mapped_column(Text)
    ai_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_status: Mapped[str] = mapped_column(String(16), default="pending")

    owner_email_status: Mapped[str] = mapped_column(String(16), default="pending")
    customer_email_status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )
