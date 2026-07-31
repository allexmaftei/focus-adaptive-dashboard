"""Database bootstrap: `flask --app backend seed`.

Gives the bundled "mock study data.csv" a purpose -- the Streamlit app never
read it, and instead hardcoded five starter rows (legacy/streamlit_app.py:24-31)
just so the charts weren't blank.
"""

from __future__ import annotations

import click
from flask import Flask, current_app

from .csv_io import load_csv, replace_sessions_from_csv
from .extensions import db
from .models import DEFAULT_SUBJECTS, StudySession, Subject


def ensure_default_subjects() -> int:
    """Add any missing default course. Returns how many were created."""
    existing = {
        name.lower()
        for name in db.session.scalars(db.select(Subject.name)).all()
    }
    created = 0
    for name in DEFAULT_SUBJECTS:
        if name.lower() not in existing:
            db.session.add(Subject(name=name))
            created += 1
    db.session.commit()
    return created


def register_cli(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db_command():
        """Create the database tables."""
        db.create_all()
        click.echo(f"Tables created in {current_app.config['SQLALCHEMY_DATABASE_URI']}")

    @app.cli.command("seed")
    @click.option(
        "--force",
        is_flag=True,
        help="Re-import the sample CSV even if sessions already exist.",
    )
    def seed_command(force: bool):
        """Create tables, add the default courses, and load the sample CSV."""
        db.create_all()

        created = ensure_default_subjects()
        click.echo(f"Default courses: {created} added, {len(DEFAULT_SUBJECTS) - created} already present.")

        existing = db.session.scalar(db.select(db.func.count(StudySession.id))) or 0
        if existing and not force:
            click.echo(f"{existing} sessions already logged; skipping sample import (use --force to replace).")
            return

        csv_path = current_app.config["SEED_CSV"]
        if not csv_path.exists():
            click.echo(f"Sample data not found at {csv_path}; nothing imported.")
            return

        imported = replace_sessions_from_csv(load_csv(csv_path))
        click.echo(f"Imported {imported} sample sessions from {csv_path.name}.")

    @app.cli.command("reset-db")
    def reset_db_command():
        """Drop every table and recreate the empty schema."""
        db.drop_all()
        db.create_all()
        click.echo("Database reset.")
