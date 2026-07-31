"""CSV import/export, shared by the seed CLI and the ``/api/data`` endpoints.

The column contract is deliberately identical to the Streamlit prototype
(legacy/streamlit_app.py:259-285) so previously exported files still restore.
"""

from __future__ import annotations

import io

import pandas as pd

from .extensions import db
from .models import BOUNDS, CSV_COLUMNS, StudySession, Subject
from .validation import ValidationError


def load_csv(source) -> pd.DataFrame:
    """Parse a CSV path/file object and verify it carries the FocusForge columns."""
    try:
        df = pd.read_csv(source)
    except Exception as exc:  # pandas raises a wide variety of parse errors
        raise ValidationError(f"Error parsing database file: {exc}") from exc

    missing = [column for column in CSV_COLUMNS if column not in df.columns]
    if missing:
        raise ValidationError(
            "Invalid database structure. File is missing standard FocusForge "
            f"column(s): {', '.join(missing)}."
        )
    return df


def _parse_rows(df: pd.DataFrame) -> list[dict]:
    """Validate every row up front so a bad file never partially imports."""
    parsed: list[dict] = []

    for offset, (_, row) in enumerate(df.iterrows()):
        line = offset + 2  # +1 for the header, +1 for 1-based numbering

        subject_name = str(row["Subject"]).strip()
        if not subject_name or subject_name.lower() == "nan":
            raise ValidationError(f"Row {line}: 'Subject' cannot be empty.")

        try:
            session_date = pd.to_datetime(row["Date"]).date()
        except Exception:
            raise ValidationError(
                f"Row {line}: 'Date' is not a valid date ({row['Date']!r})."
            ) from None

        values = {}
        for field, column in (
            ("hour", "Hour"),
            ("duration_min", "Duration_Min"),
            ("distractions", "Distractions"),
            ("focus_rating", "Focus_Rating"),
        ):
            lo, hi = BOUNDS[field]
            try:
                value = int(row[column])
            except (TypeError, ValueError):
                raise ValidationError(
                    f"Row {line}: '{column}' must be a whole number "
                    f"(got {row[column]!r})."
                ) from None
            if not lo <= value <= hi:
                raise ValidationError(
                    f"Row {line}: '{column}' must be between {lo} and {hi} (got {value})."
                )
            values[field] = value

        parsed.append({"date": session_date, "subject_name": subject_name, **values})

    return parsed


def replace_sessions_from_csv(df: pd.DataFrame) -> int:
    """Swap the whole session table for the file's contents.

    Mirrors the legacy uploader, which replaced ``study_logs`` wholesale
    (legacy/streamlit_app.py:278). Subjects referenced by the file but absent
    from the database are created. Returns the number of rows imported.
    """
    rows = _parse_rows(df)

    subjects = {
        subject.name.lower(): subject
        for subject in db.session.scalars(db.select(Subject)).all()
    }
    for row in rows:
        key = row["subject_name"].lower()
        if key not in subjects:
            subject = Subject(name=row["subject_name"])
            db.session.add(subject)
            subjects[key] = subject
    db.session.flush()  # assign ids to any newly created subjects

    db.session.query(StudySession).delete()
    for row in rows:
        db.session.add(
            StudySession(
                date=row["date"],
                hour=row["hour"],
                subject_id=subjects[row["subject_name"].lower()].id,
                duration_min=row["duration_min"],
                distractions=row["distractions"],
                focus_rating=row["focus_rating"],
            )
        )
    db.session.commit()
    return len(rows)


def export_csv() -> str:
    """Serialise every session to the legacy CSV shape."""
    sessions = (
        db.session.scalars(
            db.select(StudySession).order_by(StudySession.date, StudySession.hour)
        )
        .unique()
        .all()
    )
    df = pd.DataFrame([session.to_csv_row() for session in sessions], columns=CSV_COLUMNS)

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue()
