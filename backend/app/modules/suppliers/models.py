from datetime import datetime

from sqlalchemy import DateTime, String, UniqueConstraint, func, true
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Proveedor(Base):
    __tablename__ = "proveedor"
    __table_args__ = (
        UniqueConstraint("tipo_documento", "documento_id", name="uq_proveedor_documento"),
    )

    id_proveedor: Mapped[int] = mapped_column(primary_key=True)
    tipo_documento: Mapped[str] = mapped_column(String(45))
    documento_id: Mapped[str] = mapped_column(String(20))
    razon_social: Mapped[str] = mapped_column(String(45))
    nombre_contacto: Mapped[str] = mapped_column(String(45))
    email: Mapped[str] = mapped_column(String(150))
    telefono: Mapped[str] = mapped_column(String(20))
    direccion: Mapped[str] = mapped_column(String(150))
    ciudad: Mapped[str] = mapped_column(String(150))
    activo: Mapped[bool] = mapped_column(default=True, server_default=true())
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    ultima_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
