"""Aggregations for the dashboard.

Direct pandas ports of the Streamlit groupbys so the numbers match the
prototype exactly (legacy/streamlit_app.py:178, 199-205, 226, 239).
"""

import pandas as pd
from flask import jsonify

from ..csv_io import CSV_COLUMNS
from ..extensions import db
from ..models import StudySession
from . import api


def _empty_summary() -> dict:
    """Zeroes rather than NaN -- the legacy version crashed on an empty log."""
    return {
        "kpis": {
            "session_count": 0,
            "total_hours": 0.0,
            "avg_distractions": 0.0,
            "avg_focus": 0.0,
        },
        "focus_by_subject": [],
        "duration_by_subject": [],
        "friction_scatter": [],
        "focus_by_hour": [],
    }


@api.get("/analytics/summary")
def summary():
    sessions = db.session.scalars(db.select(StudySession)).unique().all()
    if not sessions:
        return jsonify(_empty_summary())

    df = pd.DataFrame([s.to_csv_row() for s in sessions], columns=CSV_COLUMNS)

    # KPI row (legacy/streamlit_app.py:199-201), same rounding.
    kpis = {
        "session_count": int(len(df)),
        "total_hours": round(float(df["Duration_Min"].sum()) / 60, 1),
        "avg_distractions": round(float(df["Distractions"].mean()), 1),
        "avg_focus": round(float(df["Focus_Rating"].mean()), 1),
    }

    # Mean focus per course (legacy/streamlit_app.py:178).
    focus_by_subject = (
        df.groupby("Subject")["Focus_Rating"].mean().round(2).reset_index()
    )

    # Total minutes per course. The legacy chart (legacy/streamlit_app.py:213-221)
    # was titled "Total Combined Minutes Studied" but plotted un-aggregated rows;
    # this actually sums them.
    duration_by_subject = df.groupby("Subject")["Duration_Min"].sum().reset_index()

    # Mean focus per hour of day (legacy/streamlit_app.py:239).
    focus_by_hour = df.groupby("Hour")["Focus_Rating"].mean().round(2).reset_index()

    return jsonify(
        {
            "kpis": kpis,
            "focus_by_subject": [
                {"subject": row.Subject, "focus_rating": float(row.Focus_Rating)}
                for row in focus_by_subject.itertuples()
            ],
            "duration_by_subject": [
                {"subject": row.Subject, "duration_min": int(row.Duration_Min)}
                for row in duration_by_subject.itertuples()
            ],
            # Per-session points for the distraction/focus bubble chart.
            "friction_scatter": [
                {
                    "subject": s.subject.name,
                    "distractions": s.distractions,
                    "focus_rating": s.focus_rating,
                    "duration_min": s.duration_min,
                }
                for s in sessions
            ],
            "focus_by_hour": [
                {"hour": int(row.Hour), "focus_rating": float(row.Focus_Rating)}
                for row in focus_by_hour.itertuples()
            ],
        }
    )
