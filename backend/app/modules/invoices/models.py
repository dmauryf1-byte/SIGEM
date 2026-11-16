from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Factura(Base):
    __tablename__ = "factura"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('Pendiente', 'Parcial', 'Pagada', 'Anulada')", name="ck_factura_estado"
        ),
    )

    id_factura: Mapped[int] = mapped_column(primary_key=True)
    id_cliente: Mapped[int] = mapped_column(ForeignKey("clientes.id_cliente", ondelete="RESTRICT"))
    id_vendedor: Mapped[int] = mapped_column(
        ForeignKey("vendedor.id_vendedor", ondelete="RESTRICT")
    )
    numero_factura: Mapped[str] = mapped_column(String(255), unique=True)
    fecha_factura: Mapped[datetime] = mapped_column(DateTime)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    impuesto: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    descuento: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    total_pagado: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    saldo: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    estado: Mapped[str] = mapped_column(String(45))
    notas: Mapped[str | None] = mapped_column(String(45))
    motivo_anulacion: Mapped[str | None] = mapped_column(String(255))
    fecha_anulacion: Mapped[datetime | None] = mapped_column(DateTime)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    ultima_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class DetalleFactura(Base):
    """Copia descripción, precio e IVA vigentes al facturar (AGENTS.md §3.6)."""

    __tablename__ = "detalle_factura"
    __table_args__ = (CheckConstraint("cantidad > 0", name="ck_detalle_factura_cantidad"),)

    id_detalle_factura: Mapped[int] = mapped_column(primary_key=True)
    id_factura: Mapped[int] = mapped_column(ForeignKey("factura.id_factura", ondelete="RESTRICT"))
    id_producto: Mapped[int] = mapped_column(
        ForeignKey("producto.id_producto", ondelete="RESTRICT")
    )
    descripcion: Mapped[str] = mapped_column(String(45))
    cantidad: Mapped[int]
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    descuento: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    porcentaje_impuesto: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    impuesto: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2))
