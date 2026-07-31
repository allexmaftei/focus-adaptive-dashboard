"""Course management -- replaces the Streamlit subject form
(legacy/streamlit_app.py:94-110)."""

from flask import jsonify, request

from ..extensions import db
from ..models import StudySession, Subject
from ..validation import require_payload, required_name
from . import api


def _session_counts() -> dict[int, int]:
    rows = db.session.execute(
        db.select(StudySession.subject_id, db.func.count(StudySession.id)).group_by(
            StudySession.subject_id
        )
    ).all()
    return {subject_id: count for subject_id, count in rows}


@api.get("/subjects")
def list_subjects():
    subjects = db.session.scalars(db.select(Subject).order_by(Subject.name)).all()
    counts = _session_counts()
    return jsonify([s.to_dict(session_count=counts.get(s.id, 0)) for s in subjects])


@api.post("/subjects")
def create_subject():
    data = require_payload(request.get_json(silent=True))
    name = required_name(data)

    existing = db.session.scalar(
        db.select(Subject).where(db.func.lower(Subject.name) == name.lower())
    )
    if existing is not None:
        return jsonify({"error": f"'{existing.name}' is already one of your courses."}), 409

    subject = Subject(name=name)
    db.session.add(subject)
    db.session.commit()
    return jsonify(subject.to_dict(session_count=0)), 201


@api.delete("/subjects/<int:subject_id>")
def delete_subject(subject_id: int):
    subject = db.session.get(Subject, subject_id)
    if subject is None:
        return jsonify({"error": "Course not found."}), 404

    db.session.delete(subject)  # cascades to its logged sessions
    db.session.commit()
    return "", 204
