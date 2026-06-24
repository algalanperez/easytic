"""
Tool functions que el agente llama para leer/escribir en la BD contable.
Cada función recibe y devuelve dicts planos (JSON-serializable).
"""
import hashlib
import json
from typing import Any

from database import db


_FACTURA_DEFAULTS = {
    "id": None, "numero": None, "fecha_contable": None,
    "nif_emisor": None, "nombre_emisor": None,
    "nif_receptor": None, "nombre_receptor": None,
    "base_imponible": 0.0, "tipo_iva": 21.0, "cuota_iva": 0.0,
    "tipo_retencion": 0.0, "cuota_retencion": 0.0, "total": 0.0,
    "concepto": None, "fuente": None, "fuente_id": None,
}


def tool_upsert_factura(factura: dict) -> dict:
    """
    Inserta o actualiza una factura en el libro contable.
    Genera automáticamente el id como hash de (fuente + fuente_id + fecha + total).
    """
    merged = {**_FACTURA_DEFAULTS, **factura}
    raw = f"{merged.get('fuente','')}{merged.get('fuente_id','')}{merged.get('fecha','')}{merged.get('total',0)}"
    merged.setdefault("id", hashlib.sha256(raw.encode()).hexdigest()[:24])
    if not merged["id"]:
        merged["id"] = hashlib.sha256(raw.encode()).hexdigest()[:24]
    factura = merged
    factura_id = db.upsert_factura(factura)
    # Genera asientos contables automáticos
    _auto_asientos(factura)
    return {"ok": True, "id": factura_id}


def tool_query_facturas(
    tipo: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    fuente: str | None = None,
) -> list[dict]:
    """Consulta facturas con filtros opcionales."""
    conditions = []
    params: list[Any] = []
    if tipo:
        conditions.append("tipo = ?")
        params.append(tipo)
    if fecha_desde:
        conditions.append("fecha >= ?")
        params.append(fecha_desde)
    if fecha_hasta:
        conditions.append("fecha <= ?")
        params.append(fecha_hasta)
    if fuente:
        conditions.append("fuente = ?")
        params.append(fuente)
    where = " AND ".join(conditions) if conditions else "1=1"
    return db.query_facturas(where, tuple(params))


def tool_raw_query(sql: str) -> list[dict]:
    """Ejecuta una SELECT arbitraria sobre la BD (sólo lectura)."""
    return db.raw_query(sql)


def tool_resumen_periodo(fecha_desde: str, fecha_hasta: str) -> dict:
    """
    Devuelve un resumen contable del período:
    total base, IVA devengado, IVA soportado, retenciones.
    """
    rows = db.raw_query(f"""
        SELECT
            tipo,
            ROUND(SUM(base_imponible), 2) AS base,
            ROUND(SUM(cuota_iva), 2)      AS cuota_iva,
            ROUND(SUM(cuota_retencion), 2) AS cuota_retencion,
            COUNT(*) AS n_facturas
        FROM facturas
        WHERE fecha >= '{fecha_desde}' AND fecha <= '{fecha_hasta}'
        GROUP BY tipo
    """)
    resumen: dict[str, Any] = {"periodo": {"desde": fecha_desde, "hasta": fecha_hasta}}
    for r in rows:
        resumen[r["tipo"]] = {
            "base_imponible": r["base"],
            "cuota_iva": r["cuota_iva"],
            "cuota_retencion": r["cuota_retencion"],
            "n_facturas": r["n_facturas"],
        }
    emitidas  = resumen.get("emitida",  {})
    recibidas = resumen.get("recibida", {})
    resumen["resultado_iva"] = round(
        (emitidas.get("cuota_iva", 0) or 0) - (recibidas.get("cuota_iva", 0) or 0), 2
    )
    return resumen


# ── helpers ───────────────────────────────────────────────────────────────────

def _auto_asientos(f: dict) -> None:
    """Genera asientos 477/472 básicos para IVA."""
    if not f.get("fecha"):
        return
    if f.get("tipo") == "emitida" and f.get("cuota_iva", 0):
        db.insert_asiento({
            "fecha": f["fecha"],
            "concepto": f"IVA repercutido – {f.get('concepto','factura emitida')}",
            "debe": 0,
            "haber": f["cuota_iva"],
            "cuenta": "477",
            "factura_id": f.get("id"),
        })
    elif f.get("tipo") == "recibida" and f.get("cuota_iva", 0):
        db.insert_asiento({
            "fecha": f["fecha"],
            "concepto": f"IVA soportado – {f.get('concepto','factura recibida')}",
            "debe": f["cuota_iva"],
            "haber": 0,
            "cuenta": "472",
            "factura_id": f.get("id"),
        })
