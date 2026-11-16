from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Numeric, String, func, true
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Vendedor(Base):
    __tablename__ = "vendedor"
    __table_args__ = (
        CheckConstraint(
            "porcentaje_comision BETWEEN 0 AND 100", name="ck_vendedor_porcentaje_comision"
        ),
    )

    id_vendedor: Mapped[int] = mapped_column(primary_key=True)
    tipo_documento: Mapped[str] = mapped_column(String(45))
    documento_id: Mapped[str] = mapped_column(String(45))
    nombre: Mapped[str] = mapped_column(String(75))
    email: Mapped[str] = mapped_column(String(150))
    telefono: Mapped[str] = mapped_column(String(20))
    porcentaje_comision: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    activo: Mapped[bool] = mapped_column(default=True, server_default=true())
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
