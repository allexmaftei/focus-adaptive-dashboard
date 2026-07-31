"""WSGI entrypoint for production servers: `gunicorn backend.wsgi:app`."""

from . import create_app

app = create_app()
