"""Persistent model for FocusForge.

Replaces the in-memory ``st.session_state.study_logs`` DataFrame of the
Streamlit prototype (see legacy/streamlit_app.py:19-31).
"""

from __future__ import annotations

from datetime import date as date_type, datetime, timezone

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .extensions import db

# Value bounds, mirrored from the Streamlit input widgets
# (legacy/streamlit_app.py:120-123) so the API enforces what the old UI did.
BOUNDS: dict[str, tuple[int, int]] = {
    "hour": (0, 23),
    "duration_min": (5, 240),
    "distractions": (0, 50),
    "focus_rating": (1, 5),
}

DEFAULT_SUBJECTS = ["Math", "Physics", "English", "History", "Chemistry"]

# The on-disk CSV contract. Unchanged from legacy/streamlit_app.py:276 so files
# exported by the old Streamlit app -- and the bundled "mock study data.csv" --
# still import cleanly.
CSV_COLUMNS = ["Date", "Hour", "Subject", "Duration_Min", "Distractions", "Focus_Rating"]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Subject(db.Model):
    __tablename__ = "subject"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    sessions: Mapped[list["StudySession"]] = relationship(
        back_populates="subject",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def to_dict(self, session_count: int | None = None) -> dict:
        data = {"id": self.id, "name": self.name}
        if session_count is not None:
            data["session_count"] = session_count
        return data

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Subject {self.name!r}>"


class StudySession(db.Model):
    __tablename__ = "study_session"
    __table_args__ = tuple(
        CheckConstraint(f"{field} BETWEEN {lo} AND {hi}", name=f"ck_session_{field}")
        for field, (lo, hi) in BOUNDS.items()
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    hour: Mapped[int] = mapped_column(nullable=False)
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subject.id", ondelete="CASCADE"), nullable=False, index=True
    )
    duration_min: Mapped[int] = mapped_column(nullable=False)
    distractions: Mapped[int] = mapped_column(nullable=False)
    focus_rating: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    subject: Mapped[Subject] = relationship(back_populates="sessions", lazy="joined")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "hour": self.hour,
            "subject_id": self.subject_id,
            "subject": self.subject.name,
            "duration_min": self.duration_min,
            "distractions": self.distractions,
            "focus_rating": self.focus_rating,
        }

    def to_csv_row(self) -> dict:
        """A row shaped exactly like the legacy CSV export."""
        return {
            "Date": self.date.isoformat(),
            "Hour": self.hour,
            "Subject": self.subject.name,
            "Duration_Min": self.duration_min,
            "Distractions": self.distractions,
            "Focus_Rating": self.focus_rating,
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<StudySession {self.date} {self.subject_id} {self.duration_min}min>"
