"""Application configuration.

The database URI is driven by ``DATABASE_URL`` so the SQLite default can be
swapped for Postgres without touching code.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _csv_env(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-focusforge-secret")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'focusforge.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CSV restore uploads only ever carry a few hundred rows.
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # The Vite dev server. In dev the SPA reaches the API through Vite's proxy,
    # so this only matters if the frontend is pointed straight at Flask.
    CORS_ORIGINS = _csv_env(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    )

    # Bundled sample data used by `flask --app backend seed`.
    SEED_CSV = BASE_DIR / "mock study data.csv"

    # Built SPA, served by Flask in production (`npm run build`).
    FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
