"""modelo de datos del negocio: 7 tablas del diagrama del humano (SIGEM-018)

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-16

Revisada a mano, según el diagrama del humano (docs/specs/SIGEM-018.md). Dinero en DECIMAL(14,2),
CHECK de stock, IVA, cantidad, pago y estado, y FK con RESTRICT: nada con historial se borra.
"""

from collections.abc import Sequence
from datetime import datetime

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MONEY = sa.Numeric(14, 2)
PERCENT = sa.Numeric(5, 2)


def _activo() -> sa.Column[bool]:
    return sa.Column("activo", sa.Boolean(), server_default=sa.true(), nullable=False)


def _fecha(name: str) -> sa.Column[datetime]:
    return sa.Column(name, sa.DateTime(), server_default=sa.func.now(), nullable=False)


def upgrade() -> None:
    op.create_table(
        "clientes",
        sa.Column("id_cliente", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("tipo_documento", sa.String(45), nullable=False),
        sa.Column("documento_id", sa.String(20), nullable=False),
        sa.Column("razon_social", sa.String(150), nullable=True),
        sa.Column("direccion", sa.String(100), nullable=False),
        sa.Column("telefono", sa.String(20), nullable=False),
        sa.Column("ciudad", sa.String(45), nullable=True),
        _activo(),
        _fecha("fecha_creacion"),
        _fecha("ultima_actualizacion"),
        sa.PrimaryKeyConstraint("id_cliente"),
        sa.UniqueConstraint("tipo_documento", "documento_id", name="uq_clientes_documento"),
    )
    op.create_table(
        "vendedor",
        sa.Column("id_vendedor", sa.Integer(), nullable=False),
        sa.Column("tipo_documento", sa.String(45), nullable=False),
        sa.Column("documento_id", sa.String(45), nullable=False),
        sa.Column("nombre", sa.String(75), nullable=False),
        sa.Column("email", sa.String(150), nullable=False),
        sa.Column("telefono", sa.String(20), nullable=False),
        sa.Column("porcentaje_comision", PERCENT, nullable=False),
        _activo(),
        _fecha("fecha_creacion"),
        _fecha("fecha_actualizacion"),
        sa.PrimaryKeyConstraint("id_vendedor"),
        sa.CheckConstraint(
            "porcentaje_comision BETWEEN 0 AND 100", name="ck_vendedor_porcentaje_comision"
        ),
    )
    op.create_table(
        "proveedor",
        sa.Column("id_proveedor", sa.Integer(), nullable=False),
        sa.Column("tipo_documento", sa.String(45), nullable=False),
        sa.Column("documento_id", sa.String(20), nullable=False),
        sa.Column("razon_social", sa.String(45), nullable=False),
        sa.Column("nombre_contacto", sa.String(45), nullable=False),
        sa.Column("email", sa.String(150), nullable=False),
        sa.Column("telefono", sa.String(20), nullable=False),
        sa.Column("direccion", sa.String(150), nullable=False),
        sa.Column("ciudad", sa.String(150), nullable=False),
        _activo(),
        _fecha("fecha_creacion"),
        _fecha("ultima_actualizacion"),
        sa.PrimaryKeyConstraint("id_proveedor"),
        sa.UniqueConstraint("tipo_documento", "documento_id", name="uq_proveedor_documento"),
    )
    op.create_table(
        "producto",
        sa.Column("id_producto", sa.Integer(), nullable=False),
        sa.Column("id_proveedor", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(45), nullable=False),
        sa.Column("precio_compra", MONEY, nullable=False),
        sa.Column("precio_venta", MONEY, nullable=False),
        sa.Column("porcentaje_iva", PERCENT, nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        _activo(),
        _fecha("fecha_creacion"),
        _fecha("fecha_actualizacion"),
        sa.PrimaryKeyConstraint("id_producto"),
        sa.ForeignKeyConstraint(["id_proveedor"], ["proveedor.id_proveedor"], ondelete="RESTRICT"),
        sa.CheckConstraint("stock >= 0", name="ck_producto_stock"),
        sa.CheckConstraint("porcentaje_iva IN (0, 5, 19)", name="ck_producto_porcentaje_iva"),
    )
    op.create_table(
        "factura",
        sa.Column("id_factura", sa.Integer(), nullable=False),
        sa.Column("id_cliente", sa.Integer(), nullable=False),
        sa.Column("id_vendedor", sa.Integer(), nullable=False),
        sa.Column("numero_factura", sa.String(255), nullable=False),
        sa.Column("fecha_factura", sa.DateTime(), nullable=False),
        sa.Column("subtotal", MONEY, nullable=False),
        sa.Column("impuesto", MONEY, nullable=False),
        sa.Column("descuento", MONEY, nullable=False),
        sa.Column("total", MONEY, nullable=False),
        sa.Column("total_pagado", MONEY, nullable=False),
        sa.Column("saldo", MONEY, nullable=False),
        sa.Column("estado", sa.String(45), nullable=False),
        sa.Column("notas", sa.String(45), nullable=True),
        sa.Column("motivo_anulacion", sa.String(255), nullable=True),
        sa.Column("fecha_anulacion", sa.DateTime(), nullable=True),
        _fecha("fecha_creacion"),
        _fecha("ultima_actualizacion"),
        sa.PrimaryKeyConstraint("id_factura"),
        sa.ForeignKeyConstraint(["id_cliente"], ["clientes.id_cliente"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_vendedor"], ["vendedor.id_vendedor"], ondelete="RESTRICT"),
        sa.UniqueConstraint("numero_factura"),
        sa.CheckConstraint(
            "estado IN ('Pendiente', 'Parcial', 'Pagada', 'Anulada')", name="ck_factura_estado"
        ),
    )
    op.create_table(
        "detalle_factura",
        sa.Column("id_detalle_factura", sa.Integer(), nullable=False),
        sa.Column("id_factura", sa.Integer(), nullable=False),
        sa.Column("id_producto", sa.Integer(), nullable=False),
        sa.Column("descripcion", sa.String(45), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("precio_unitario", MONEY, nullable=False),
        sa.Column("descuento", MONEY, nullable=False),
        sa.Column("porcentaje_impuesto", PERCENT, nullable=False),
        sa.Column("impuesto", MONEY, nullable=False),
        sa.Column("subtotal", MONEY, nullable=False),
        sa.Column("total", MONEY, nullable=False),
        sa.PrimaryKeyConstraint("id_detalle_factura"),
        sa.ForeignKeyConstraint(["id_factura"], ["factura.id_factura"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_producto"], ["producto.id_producto"], ondelete="RESTRICT"),
        sa.CheckConstraint("cantidad > 0", name="ck_detalle_factura_cantidad"),
    )
    op.create_table(
        "pagos",
        sa.Column("id_pago", sa.Integer(), nullable=False),
        sa.Column("id_factura", sa.Integer(), nullable=False),
        sa.Column("fecha_pago", sa.DateTime(), nullable=False),
        sa.Column("valor", MONEY, nullable=False),
        sa.Column("metodo_pago", sa.String(45), nullable=False),
        sa.Column("referencia", sa.String(45), nullable=True),
        sa.Column("notas", sa.String(45), nullable=True),
        _fecha("fecha_creacion"),
        sa.PrimaryKeyConstraint("id_pago"),
        sa.ForeignKeyConstraint(["id_factura"], ["factura.id_factura"], ondelete="RESTRICT"),
        sa.CheckConstraint("valor > 0", name="ck_pagos_valor"),
    )


def downgrade() -> None:
    for table in (
        "pagos",
        "detalle_factura",
        "factura",
        "producto",
        "proveedor",
        "vendedor",
        "clientes",
    ):
        op.drop_table(table)
