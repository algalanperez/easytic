import sqlite3
import json
from pathlib import Path
from typing import Any

import config

_conn: sqlite3.Connection | None = None


def get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA foreign_keys=ON")
        _init_schema()
    return _conn


def _init_schema() -> None:
    schema = (Path(__file__).parent / "schema.sql").read_text()
    get_conn().executescript(schema)
    get_conn().commit()


# ── Facturas ──────────────────────────────────────────────────────────────────

def upsert_factura(factura: dict) -> str:
    """Inserta o actualiza una factura. Devuelve su id."""
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO facturas
            (id, tipo, numero, fecha, fecha_contable, nif_emisor, nombre_emisor,
             nif_receptor, nombre_receptor, base_imponible, tipo_iva, cuota_iva,
             tipo_retencion, cuota_retencion, total, concepto, fuente, fuente_id)
        VALUES
            (:id, :tipo, :numero, :fecha, :fecha_contable, :nif_emisor, :nombre_emisor,
             :nif_receptor, :nombre_receptor, :base_imponible, :tipo_iva, :cuota_iva,
             :tipo_retencion, :cuota_retencion, :total, :concepto, :fuente, :fuente_id)
        ON CONFLICT(id) DO UPDATE SET
            numero          = excluded.numero,
            fecha_contable  = excluded.fecha_contable,
            base_imponible  = excluded.base_imponible,
            tipo_iva        = excluded.tipo_iva,
            cuota_iva       = excluded.cuota_iva,
            tipo_retencion  = excluded.tipo_retencion,
            cuota_retencion = excluded.cuota_retencion,
            total           = excluded.total,
            concepto        = excluded.concepto
        """,
        factura,
    )
    conn.commit()
    return factura["id"]


def query_facturas(sql_where: str = "1=1", params: tuple = ()) -> list[dict]:
    rows = get_conn().execute(
        f"SELECT * FROM facturas WHERE {sql_where}", params
    ).fetchall()
    return [dict(r) for r in rows]


# ── Asientos ─────────────────────────────────────────────────────────────────

def insert_asiento(asiento: dict) -> int:
    conn = get_conn()
    cur = conn.execute(
        """
        INSERT INTO asientos (fecha, concepto, debe, haber, cuenta, factura_id)
        VALUES (:fecha, :concepto, :debe, :haber, :cuenta, :factura_id)
        """,
        asiento,
    )
    conn.commit()
    return cur.lastrowid


# ── Liquidaciones ─────────────────────────────────────────────────────────────

def upsert_liquidacion(modelo: str, ejercicio: int, periodo: str, datos: dict) -> None:
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO liquidaciones (modelo, ejercicio, periodo, datos_json)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(modelo, ejercicio, periodo) DO UPDATE SET
            datos_json = excluded.datos_json,
            estado     = 'borrador'
        """,
        (modelo, ejercicio, periodo, json.dumps(datos, ensure_ascii=False)),
    )
    conn.commit()


def get_liquidacion(modelo: str, ejercicio: int, periodo: str) -> dict | None:
    row = get_conn().execute(
        "SELECT * FROM liquidaciones WHERE modelo=? AND ejercicio=? AND periodo=?",
        (modelo, ejercicio, periodo),
    ).fetchone()
    if row is None:
        return None
    d = dict(row)
    d["datos"] = json.loads(d["datos_json"] or "{}")
    return d


# ── Consultas genéricas (para el agente) ─────────────────────────────────────

def raw_query(sql: str) -> list[dict]:
    """Ejecuta SQL de sólo lectura y devuelve filas como dicts."""
    if any(w in sql.upper() for w in ("INSERT", "UPDATE", "DELETE", "DROP", "CREATE")):
        raise ValueError("raw_query sólo admite SELECT")
    rows = get_conn().execute(sql).fetchall()
    return [dict(r) for r in rows]
