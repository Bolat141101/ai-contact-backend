from datetime import UTC, datetime, timedelta

from sqlalchemy import func, or_, select

from app.extensions import db
from app.models.contact import Contact


class MetricsRepository:
    def get_summary(self) -> dict:
        since = datetime.now(UTC) - timedelta(hours=24)

        total = db.session.scalar(select(func.count(Contact.id))) or 0
        recent = (
            db.session.scalar(select(func.count(Contact.id)).where(Contact.created_at >= since))
            or 0
        )
        ai_fallbacks = (
            db.session.scalar(select(func.count(Contact.id)).where(Contact.ai_processed.is_(False)))
            or 0
        )
        email_failures = (
            db.session.scalar(
                select(func.count(Contact.id)).where(
                    or_(
                        Contact.owner_email_status == "failed",
                        Contact.customer_email_status == "failed",
                    )
                )
            )
            or 0
        )
        category_rows = db.session.execute(
            select(Contact.category, func.count(Contact.id)).group_by(Contact.category)
        ).all()

        return {
            "total": total,
            "last_24_hours": recent,
            "ai_fallbacks": ai_fallbacks,
            "email_failures": email_failures,
            "by_category": dict(category_rows),
        }
