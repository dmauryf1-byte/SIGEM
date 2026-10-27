from datetime import UTC, datetime


def utcnow() -> datetime:
    """Hora UTC sin zona y sin microsegundos: así la guarda DATETIME de MySQL.

    MySQL redondea las fracciones de segundo al guardar; truncar aquí evita que un vencimiento
    calculado en Python difiera en un segundo del guardado.
    """
    return datetime.now(UTC).replace(tzinfo=None, microsecond=0)
