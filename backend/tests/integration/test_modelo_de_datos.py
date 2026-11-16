"""SIGEM-018: la BD misma rechaza datos inválidos, aunque un service se equivoque."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import inspect, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.core.db import Base
from app.modules.customers import models as _customers  # noqa: F401  registran las tablas en Base
from app.modules.invoices import models as _invoices  # noqa: F401
from app.modules.payments import models as _payments  # noqa: F401
from app.modules.products import models as _products  # noqa: F401
from app.modules.salespeople import models as _salespeople  # noqa: F401
from app.modules.suppliers import models as _suppliers  # noqa: F401
from tests.conftest import ALEMBIC_INI, TEST_DATABASE, test_engine

TABLAS = {"clientes", "vendedor", "proveedor", "producto", "factura", "detalle_factura", "pagos"}

# Códigos de error de MySQL
CHECK_VIOLADO = 3819
FK_INEXISTENTE = 1452
FILA_CON_HIJOS = 1451
DUPLICADO = 1062


def sql(db: Session, statement: str, **params: Any) -> int:
    result = db.connection().execute(text(statement), params)
    db.commit()
    return result.lastrowid


@contextmanager
def rechaza(db: Session, codigo: int) -> Iterator[None]:
    with pytest.raises(DBAPIError) as exc:
        yield
    db.rollback()
    assert exc.value.orig is not None
    assert exc.value.orig.args[0] == codigo


def cliente(db: Session, documento: str = "1010") -> int:
    return sql(
        db,
        "INSERT INTO clientes (nombre, tipo_documento, documento_id, direccion, telefono)"
        " VALUES ('Ana', 'CC', :doc, 'Calle 1', '3001234567')",
        doc=documento,
    )


def vendedor(db: Session, comision: int = 5) -> int:
    return sql(
        db,
        "INSERT INTO vendedor (tipo_documento, documento_id, nombre, email, telefono,"
        " porcentaje_comision) VALUES ('CC', '2020', 'Luis', 'l@x.co', '3100000000', :c)",
        c=comision,
    )


def producto(db: Session, stock: int = 3, iva: int = 19) -> int:
    proveedor = sql(
        db,
        "INSERT INTO proveedor (tipo_documento, documento_id, razon_social, nombre_contacto,"
        " email, telefono, direccion, ciudad)"
        " VALUES ('NIT', '900123456-7', 'Acme', 'Eva', 'e@x.co', '6011234567', 'Cra 2', 'Bogotá')",
    )
    return sql(
        db,
        "INSERT INTO producto (id_proveedor, nombre, precio_compra, precio_venta, porcentaje_iva,"
        " stock) VALUES (:p, 'Lápiz', 800.00, 1200.50, :iva, :stock)",
        p=proveedor,
        iva=iva,
        stock=stock,
    )


def factura(db: Session, numero: str = "F-1", estado: str = "Pendiente") -> int:
    return sql(
        db,
        "INSERT INTO factura (id_cliente, id_vendedor, numero_factura, fecha_factura, subtotal,"
        " impuesto, descuento, total, total_pagado, saldo, estado)"
        " VALUES (:c, :v, :n, NOW(), 1000, 190, 0, 1190, 0, 1190, :e)",
        c=cliente(db, documento=f"doc-{numero}"),
        v=vendedor(db),
        n=numero,
        e=estado,
    )


def detalle(db: Session, id_factura: int, id_producto: int, cantidad: int = 1) -> int:
    return sql(
        db,
        "INSERT INTO detalle_factura (id_factura, id_producto, descripcion, cantidad,"
        " precio_unitario, descuento, porcentaje_impuesto, impuesto, subtotal, total)"
        " VALUES (:f, :p, 'Lápiz', :c, 1000, 0, 19, 190, 1000, 1190)",
        f=id_factura,
        p=id_producto,
        c=cantidad,
    )


def pago(db: Session, id_factura: int, valor: str) -> int:
    return sql(
        db,
        "INSERT INTO pagos (id_factura, fecha_pago, valor, metodo_pago)"
        " VALUES (:f, NOW(), :v, 'Efectivo')",
        f=id_factura,
        v=valor,
    )


def test_flujo_valido_guarda_montos_exactos(db: Session) -> None:
    id_factura = factura(db)
    detalle(db, id_factura, producto(db))
    pago(db, id_factura, "0.10")
    pago(db, id_factura, "0.20")

    assert str(db.execute(text("SELECT SUM(valor) FROM pagos")).scalar()) == "0.30"
    assert str(db.execute(text("SELECT precio_venta FROM producto")).scalar()) == "1200.50"


def test_stock_negativo(db: Session) -> None:
    id_producto = producto(db, stock=1)
    with rechaza(db, CHECK_VIOLADO):
        sql(db, "UPDATE producto SET stock = stock - 2 WHERE id_producto = :p", p=id_producto)


@pytest.mark.parametrize("iva", [0, 5, 19])
def test_iva_permitido(db: Session, iva: int) -> None:
    producto(db, iva=iva)


def test_iva_invalido(db: Session) -> None:
    with rechaza(db, CHECK_VIOLADO):
        producto(db, iva=16)


@pytest.mark.parametrize("cantidad", [0, -1])
def test_cantidad_debe_ser_positiva(db: Session, cantidad: int) -> None:
    id_factura, id_producto = factura(db), producto(db)
    with rechaza(db, CHECK_VIOLADO):
        detalle(db, id_factura, id_producto, cantidad=cantidad)


@pytest.mark.parametrize("valor", ["0", "-5.00"])
def test_pago_debe_ser_positivo(db: Session, valor: str) -> None:
    id_factura = factura(db)
    with rechaza(db, CHECK_VIOLADO):
        pago(db, id_factura, valor)


@pytest.mark.parametrize("estado", ["Pendiente", "Parcial", "Pagada", "Anulada"])
def test_estado_permitido(db: Session, estado: str) -> None:
    factura(db, estado=estado)


def test_estado_invalido(db: Session) -> None:
    with rechaza(db, CHECK_VIOLADO):
        factura(db, estado="Borrada")


def test_comision_fuera_de_rango(db: Session) -> None:
    with rechaza(db, CHECK_VIOLADO):
        vendedor(db, comision=101)


def test_fk_inexistente(db: Session) -> None:
    with rechaza(db, FK_INEXISTENTE):
        pago(db, id_factura=999, valor="10")


def test_documento_de_cliente_repetido(db: Session) -> None:
    cliente(db, documento="123")
    with rechaza(db, DUPLICADO):
        cliente(db, documento="123")


def test_numero_de_factura_repetido(db: Session) -> None:
    factura(db, numero="F-9")
    with rechaza(db, DUPLICADO):
        sql(
            db,
            "INSERT INTO factura (id_cliente, id_vendedor, numero_factura, fecha_factura,"
            " subtotal, impuesto, descuento, total, total_pagado, saldo, estado)"
            " SELECT id_cliente, id_vendedor, 'F-9', NOW(), 0, 0, 0, 0, 0, 0, 'Pendiente'"
            " FROM factura",
        )


def test_no_se_borra_cliente_con_facturas(db: Session) -> None:
    factura(db)
    with rechaza(db, FILA_CON_HIJOS):
        sql(db, "DELETE FROM clientes")


def test_modelos_coinciden_con_la_migracion() -> None:
    with test_engine.connect() as connection:
        diferencias = compare_metadata(MigrationContext.configure(connection), Base.metadata)
    assert diferencias == []


def test_downgrade_borra_solo_las_tablas_nuevas() -> None:
    config = Config(str(ALEMBIC_INI))
    config.attributes["database"] = TEST_DATABASE
    test_engine.dispose()  # suelta conexiones abiertas que bloquearían el DROP
    command.downgrade(config, "0001")
    try:
        tablas = set(inspect(test_engine).get_table_names())
        assert not tablas & TABLAS
        assert {"users", "refresh_tokens"} <= tablas
    finally:
        test_engine.dispose()
        command.upgrade(config, "head")
    assert TABLAS <= set(inspect(test_engine).get_table_names())
