from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func, true
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Producto(Base):
    __tablename__ = "producto"
    __table_args__ = (
        CheckConstraint("stock >= 0", name="ck_producto_stock"),
        CheckConstraint("porcentaje_iva IN (0, 5, 19)", name="ck_producto_porcentaje_iva"),
    )

    id_producto: Mapped[int] = mapped_column(primary_key=True)
    id_proveedor: Mapped[int] = mapped_column(
        ForeignKey("proveedor.id_proveedor", ondelete="RESTRICT")
    )
    nombre: Mapped[str] = mapped_column(String(45))
    precio_compra: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    precio_venta: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    porcentaje_iva: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    stock: Mapped[int]
    activo: Mapped[bool] = mapped_column(default=True, server_default=true())
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
