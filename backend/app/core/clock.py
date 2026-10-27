from datetime import UTC, datetime


def utcnow() -> datetime:
    """Hora UTC sin zona: así la guarda y la devuelve DATETIME de MySQL."""
    return datetime.now(UTC).replace(tzinfo=None)
