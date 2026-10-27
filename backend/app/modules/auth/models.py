from datetime import datetime

from sqlalchemy import CHAR, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class RefreshToken(Base):
    """Token de renovación: se guarda solo su hash. Los de un mismo login comparten session_id."""

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[str] = mapped_column(String(43), index=True)
    token_hash: Mapped[str] = mapped_column(CHAR(64), unique=True)
    session_started_at: Mapped[datetime] = mapped_column(DateTime)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
