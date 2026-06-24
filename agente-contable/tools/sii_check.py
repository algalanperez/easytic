"""
Verificación de cumplimiento SII / Verifactu para facturas registradas.

Comprueba los campos mínimos requeridos por:
  - SII (Suministro Inmediato de Información, RD 596/2016)
  - Verifactu (RD 1007/2023, obligatorio desde 2025 para empresas no SII)

No genera el hash ni envía a la AEAT — eso requiere certificado digital
y conexión a Sede Electrónica. Este módulo detecta incidencias previas
para que puedas corregirlas antes de presentar.
"""
from __future__ import annotations

import re
from typing import Any

from database import db

# Campos obligatorios SII mínimos por tipo de factura
_REQUIRED: dict[str, str] = {
    "numero":        "Número de factura",
    "fecha":         "Fecha de expedición",
    "nif_emisor":    "NIF del emisor",
    "nombre_emisor": "Nombre/razón social del emisor",
    "base_imponible":"Base imponible",
    "cuota_iva":     "Cuota de IVA",
    "total":         "Importe total",
}

_TIPOS_IVA_VALIDOS = {0.0, 4.0, 10.0, 21.0}
_RE_NIF = re.compile(r"^[A-Z0-9]{8,9}[A-Z0-9]$", re.IGNORECASE)
_RE_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def check_sii_compliance(
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    tipo: str | None = None,        # 'emitida' | 'recibida' | None → ambas
) -> dict[str, Any]:
    """
    Verifica el cumplimiento SII/Verifactu de las facturas en el rango indicado.

    Devuelve un informe con: resumen, listado de errores por factura y recomendaciones.
    """
    conds = ["1=1"]
    if fecha_desde:
        conds.append(f"fecha >= '{fecha_desde}'")
    if fecha_hasta:
        conds.append(f"fecha <= '{fecha_hasta}'")
    if tipo:
        conds.append(f"tipo = '{tipo}'")

    facturas = db.raw_query(
        f"SELECT * FROM facturas WHERE {' AND '.join(conds)} ORDER BY fecha, tipo"
    )

    ok_ids: list[str] = []
    errores: list[dict] = []

    for f in facturas:
        issues = _check_factura(f)
        if issues:
            errores.append({
                "id":      f["id"],
                "numero":  f["numero"] or "(sin número)",
                "fecha":   f["fecha"],
                "tipo":    f["tipo"],
                "emisor":  f["nombre_emisor"] or f["nif_emisor"] or "(desconocido)",
                "total":   f["total"],
                "errores": issues,
            })
        else:
            ok_ids.append(f["id"])

    n_total   = len(facturas)
    n_errores = len(errores)
    pct_ok    = round((len(ok_ids) / n_total * 100) if n_total else 100.0, 1)

    return {
        "periodo": {"desde": fecha_desde, "hasta": fecha_hasta, "tipo": tipo},
        "resumen": {
            "total_facturas":        n_total,
            "facturas_ok":           len(ok_ids),
            "facturas_con_errores":  n_errores,
            "porcentaje_cumplimiento": pct_ok,
        },
        "facturas_error": errores,
        "facturas_ok_ids": ok_ids,
        "recomendaciones": _recomendaciones(errores),
    }


# ── validación individual ─────────────────────────────────────────────────────

def _check_factura(f: dict) -> list[str]:
    issues: list[str] = []

    # 1. Campos obligatorios presentes y no vacíos
    for field, label in _REQUIRED.items():
        val = f.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            issues.append(f"Campo obligatorio vacío: {label}")
        elif isinstance(val, (int, float)) and field in ("base_imponible", "cuota_iva", "total") and val < 0:
            issues.append(f"{label} es negativo ({val:.2f} €). Usa factura rectificativa (Tipo R1).")

    # 2. Formato NIF (solo advertencia si existe pero tiene formato raro)
    for nif_field in ("nif_emisor", "nif_receptor"):
        nif = f.get(nif_field) or ""
        if nif and not _RE_NIF.match(nif.replace(" ", "").replace("-", "")):
            issues.append(f"Formato de NIF posiblemente incorrecto: {nif_field} = '{nif}'.")

    # 3. Tipo de IVA válido
    tipo_iva = f.get("tipo_iva")
    if tipo_iva is not None and float(tipo_iva) not in _TIPOS_IVA_VALIDOS:
        issues.append(
            f"Tipo de IVA inusual: {tipo_iva}%. "
            "Los tipos vigentes en España son 0%, 4%, 10% y 21%."
        )

    # 4. Coherencia base + cuota − retención ≈ total
    base = float(f.get("base_imponible") or 0)
    cuota = float(f.get("cuota_iva") or 0)
    ret   = float(f.get("cuota_retencion") or 0)
    total = float(f.get("total") or 0)
    if total > 0:
        esperado = round(base + cuota - ret, 2)
        if abs(esperado - total) > 1.0:
            issues.append(
                f"Total inconsistente: {base:.2f} + {cuota:.2f} (IVA) "
                f"− {ret:.2f} (ret.) = {esperado:.2f} €, pero total registrado = {total:.2f} €."
            )

    # 5. Formato de fecha ISO
    fecha = f.get("fecha") or ""
    if fecha and not _RE_FECHA.match(fecha):
        issues.append(f"Formato de fecha incorrecto: '{fecha}'. Debe ser YYYY-MM-DD.")

    return issues


def _recomendaciones(errores: list[dict]) -> list[str]:
    if not errores:
        return ["Todas las facturas cumplen los requisitos mínimos SII/Verifactu."]

    recs: list[str] = [
        f"Hay {len(errores)} factura(s) con incidencias. "
        "Corrígelas antes de presentar el Modelo 303 o el SII."
    ]
    campos_faltantes = {
        issue
        for f in errores
        for issue in f["errores"]
        if "vacío" in issue
    }
    if any("NIF del emisor" in c for c in campos_faltantes):
        recs.append(
            "Varias facturas carecen de NIF del emisor — campo obligatorio SII. "
            "Solicita los datos a tus proveedores o clientes."
        )
    if any("Número de factura" in c for c in campos_faltantes):
        recs.append(
            "Hay facturas sin número. Asigna numeración correlativa: "
            "el SII rechaza registros sin número de factura."
        )
    if any("Total inconsistente" in issue for f in errores for issue in f["errores"]):
        recs.append(
            "Totales inconsistentes detectados. Revisa si la retención de IRPF "
            "está correctamente registrada o si hay redondeos en los PDFs originales."
        )
    return recs
