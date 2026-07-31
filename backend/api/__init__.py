from flask import Blueprint

api = Blueprint("api", __name__, url_prefix="/api")

# Imported for their side effect of registering routes on the blueprint.
from . import analytics, data, sessions, subjects  # noqa: E402,F401
