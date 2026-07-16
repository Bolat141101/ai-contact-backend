from flask import current_app, request
from flask.views import MethodView
from flask_smorest import Blueprint

from app.extensions import limiter
from app.schemas.contact import ContactCreateSchema, ContactResponseSchema
from app.services.contact_service import ContactService

blueprint = Blueprint(
    "contact",
    __name__,
    url_prefix="/api",
    description="Contact form submission",
)


@blueprint.route("/contact")
class ContactResource(MethodView):
    @blueprint.arguments(ContactCreateSchema)
    @blueprint.response(201, ContactResponseSchema)
    @limiter.limit(lambda: current_app.config["CONTACT_RATE_LIMIT"])
    def post(self, data):
        """Validate, enrich, persist, and notify about a contact request."""
        return ContactService().create_contact(data, request.remote_addr)
