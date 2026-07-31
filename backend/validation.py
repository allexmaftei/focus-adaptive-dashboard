"""Payload validation shared by the API blueprints."""

from __future__ import annotations

from datetime import date, datetime

from .models import BOUNDS


class ValidationError(ValueError):
    """Raised on bad request payloads; converted to a 400 by the app factory."""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(message)
        self.message = message
        self.field = field


def require_payload(data) -> dict:
    if not isinstance(data, dict):
        raise ValidationError("Expected a JSON object body.")
    return data


def bounded_int(data: dict, key: str, *, default: int | None = None) -> int:
    """Read ``key`` and check it against the shared BOUNDS table."""
    lo, hi = BOUNDS[key]
    raw = data.get(key, default)
    if raw is None:
        raise ValidationError(f"'{key}' is required.", field=key)
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise ValidationError(f"'{key}' must be a whole number.", field=key) from None
    if not lo <= value <= hi:
        raise ValidationError(f"'{key}' must be between {lo} and {hi}.", field=key)
    return value


def required_date(data: dict, key: str = "date") -> date:
    raw = data.get(key)
    if raw is None:
        raise ValidationError(f"'{key}' is required.", field=key)
    if isinstance(raw, date) and not isinstance(raw, datetime):
        return raw
    try:
        return date.fromisoformat(str(raw)[:10])
    except ValueError:
        raise ValidationError(
            f"'{key}' must be an ISO date (YYYY-MM-DD).", field=key
        ) from None


def required_name(data: dict, key: str = "name", max_len: int = 80) -> str:
    raw = data.get(key)
    name = str(raw).strip() if raw is not None else ""
    if not name:
        raise ValidationError(f"'{key}' cannot be empty.", field=key)
    if len(name) > max_len:
        raise ValidationError(f"'{key}' must be {max_len} characters or fewer.", field=key)
    return name
