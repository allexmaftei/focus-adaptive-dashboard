"""FocusForge API.

Application factory. Run the dev server with:

    flask --app backend --debug run
"""

from __future__ import annotations

import sqlite3

from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from sqlalchemy import event
from sqlalchemy.engine import Engine
from werkzeug.exceptions import HTTPException

from .config import Config
from .extensions import cors, db
from .validation import ValidationError

load_dotenv()


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _record):
    """SQLite ignores FK constraints unless asked; needed for ON DELETE CASCADE."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_app(config_object: type[Config] = Config) -> Flask:
    # static_folder is disabled: the SPA catch-all below serves the built assets.
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_object)

    db.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
    )

    from .api import api
    from .seed import register_cli

    app.register_blueprint(api)
    register_cli(app)
    _register_error_handlers(app)
    _register_spa(app)

    with app.app_context():
        db.create_all()

    return app


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        payload = {"error": error.message}
        if error.field:
            payload["field"] = error.field
        return jsonify(payload), 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        return jsonify({"error": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected(error: Exception):
        app.logger.exception("Unhandled error")
        db.session.rollback()
        return jsonify({"error": "Internal server error."}), 500


def _register_spa(app: Flask) -> None:
    """Serve the Vite build in production. In dev the SPA is served by Vite on
    :5173 and proxies /api here, so this only fires once `npm run build` has run."""
    dist = app.config["FRONTEND_DIST"]

    @app.get("/", defaults={"path": ""})
    @app.get("/<path:path>")
    def spa(path: str):
        # Unknown API routes must stay JSON 404s rather than falling through to
        # index.html, which would hand the client HTML it can't parse.
        if path.startswith("api/"):
            return jsonify({"error": "Unknown API endpoint."}), 404
        if path and (dist / path).is_file():
            return send_from_directory(dist, path)
        if (dist / "index.html").is_file():
            return send_from_directory(dist, "index.html")
        return (
            jsonify(
                {
                    "service": "FocusForge API",
                    "hint": "No frontend build found. Run the Vite dev server "
                    "(cd frontend && npm run dev) or build it (npm run build).",
                    "api": "/api/subjects, /api/sessions, /api/analytics/summary",
                }
            ),
            200,
        )
