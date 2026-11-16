from datetime import datetime

from sqlalchemy import DateTime, String, UniqueConstraint, func, true
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Cliente(Base):
    __tablename__ = "clientes"
    __table_args__ = (
        UniqueConstraint("tipo_documento", "documento_id", name="uq_clientes_documento"),
    )

    id_cliente: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255))
    tipo_documento: Mapped[str] = mapped_column(String(45))
    documento_id: Mapped[str] = mapped_column(String(20))
    razon_social: Mapped[str | None] = mapped_column(String(150))
    direccion: Mapped[str] = mapped_column(String(100))
    telefono: Mapped[str] = mapped_column(String(20))
    ciudad: Mapped[str | None] = mapped_column(String(45))
    activo: Mapped[bool] = mapped_column(default=True, server_default=true())
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    ultima_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
