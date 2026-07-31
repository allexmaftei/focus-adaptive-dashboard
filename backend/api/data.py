"""CSV portability -- replaces the Streamlit download/upload pair
(legacy/streamlit_app.py:259-285). Persistence makes this a backup feature
rather than the only way to keep data."""

from flask import Response, jsonify, request

from ..csv_io import export_csv, load_csv, replace_sessions_from_csv
from ..validation import ValidationError
from . import api

EXPORT_FILENAME = "focusforge_database.csv"


@api.get("/data/export")
def export_data():
    return Response(
        export_csv(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{EXPORT_FILENAME}"'},
    )


@api.post("/data/import")
def import_data():
    upload = request.files.get("file")
    if upload is None or not upload.filename:
        raise ValidationError("No CSV file was uploaded (expected form field 'file').")
    if not upload.filename.lower().endswith(".csv"):
        raise ValidationError("Only .csv files can be restored.")

    df = load_csv(upload.stream)
    imported = replace_sessions_from_csv(df)
    return jsonify(
        {
            "imported": imported,
            "message": f"Successfully imported {imported} sessions. All metrics updated.",
        }
    )
