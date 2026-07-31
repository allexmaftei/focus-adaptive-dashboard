"""Study session logging -- replaces the Streamlit log form
(legacy/streamlit_app.py:116-140)."""

from flask import jsonify, request

from ..extensions import db
from ..models import StudySession, Subject
from ..validation import (
    ValidationError,
    bounded_int,
    require_payload,
    required_date,
)
from . import api


def _resolve_subject(data: dict) -> Subject:
    """Accept either a subject_id or a subject name, as the form may send either."""
    subject_id = data.get("subject_id")
    if subject_id is not None:
        subject = db.session.get(Subject, subject_id)
        if subject is None:
            raise ValidationError("Unknown course.", field="subject_id")
        return subject

    name = data.get("subject")
    if name:
        subject = db.session.scalar(
            db.select(Subject).where(db.func.lower(Subject.name) == str(name).strip().lower())
        )
        if subject is None:
            raise ValidationError(f"Unknown course '{name}'.", field="subject")
        return subject

    raise ValidationError("'subject_id' is required.", field="subject_id")


@api.get("/sessions")
def list_sessions():
    query = db.select(StudySession).order_by(
        StudySession.date.desc(), StudySession.hour.desc(), StudySession.id.desc()
    )

    subject_id = request.args.get("subject_id", type=int)
    if subject_id is not None:
        query = query.where(StudySession.subject_id == subject_id)

    sessions = db.session.scalars(query).unique().all()
    return jsonify([s.to_dict() for s in sessions])


@api.post("/sessions")
def create_session():
    data = require_payload(request.get_json(silent=True))
    subject = _resolve_subject(data)

    session = StudySession(
        date=required_date(data),
        hour=bounded_int(data, "hour"),
        subject_id=subject.id,
        duration_min=bounded_int(data, "duration_min"),
        distractions=bounded_int(data, "distractions"),
        focus_rating=bounded_int(data, "focus_rating"),
    )
    db.session.add(session)
    db.session.commit()
    return jsonify(session.to_dict()), 201


@api.delete("/sessions/<int:session_id>")
def delete_session(session_id: int):
    session = db.session.get(StudySession, session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404

    db.session.delete(session)
    db.session.commit()
    return "", 204
