from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Pago(Base):
    __tablename__ = "pagos"
    __table_args__ = (CheckConstraint("valor > 0", name="ck_pagos_valor"),)

    id_pago: Mapped[int] = mapped_column(primary_key=True)
    id_factura: Mapped[int] = mapped_column(ForeignKey("factura.id_factura", ondelete="RESTRICT"))
    fecha_pago: Mapped[datetime] = mapped_column(DateTime)
    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    metodo_pago: Mapped[str] = mapped_column(String(45))
    referencia: Mapped[str | None] = mapped_column(String(45))
    notas: Mapped[str | None] = mapped_column(String(45))
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
