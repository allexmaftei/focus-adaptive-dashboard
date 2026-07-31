"""Extension instances, kept separate so models and blueprints can import ``db``
without importing the application factory."""

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base."""


db = SQLAlchemy(model_class=Base)
cors = CORS()
