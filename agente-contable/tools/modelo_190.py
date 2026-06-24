"""
Modelo 190 — Resumen Anual de Retenciones e Ingresos a Cuenta (IRPF).

Es el consolidado anual de los cuatro Modelos 111 trimestrales.
Incluye la relación nominal de perceptores con sus datos anuales.
Plazo: 31 de enero del año siguiente al ejercicio.

Clave de percepción usada:
  G — Rendimientos de actividades profesionales (autónomos / freelance)
      IRPF tipo habitual 15 % (7 % en inicio de actividad)

Casillas de resumen implementadas:
  Total perceptores (únicos por NIF/nombre en el ejercicio)
  Total base de retención
  Total retenciones ingresadas
  Relación nominal de perceptores con desglose anual
"""
from __future__ import annotations

from typing import Any

import config
from database import db


def calculate_190(ejercicio: int) -> dict[str, Any]:
    """
    Calcula el Modelo 190 (resumen anual retenciones IRPF).

    Agrega todas las facturas recibidas con retención del ejercicio y genera
    la relación nominal de perceptores.
    """
    fecha_desde = f"{ejercicio}-01-01"
    fecha_hasta = f"{ejercicio}-12-31"

    # ── Totales anuales ───────────────────────────────────────────────────────
    totales = db.raw_query(f"""
        SELECT
            COUNT(DISTINCT COALESCE(nif_emisor, nombre_emisor, fuente_id)) AS n_perceptores,
            ROUND(SUM(base_imponible), 2)  AS base_total,
            ROUND(SUM(cuota_retencion), 2) AS retenciones_total
        FROM facturas
        WHERE tipo = 'recibida'
          AND cuota_retencion > 0
          AND fecha >= '{fecha_desde}' AND fecha <= '{fecha_hasta}'
    """)[0]

    n_perceptores     = totales["n_perceptores"]    or 0
    base_total        = totales["base_total"]       or 0.0
    retenciones_total = totales["retenciones_total"] or 0.0

    # ── Relación nominal de perceptores ───────────────────────────────────────
    # Agrupamos por NIF primero (si hay NIF), luego por nombre como fallback
    perceptores_rows = db.raw_query(f"""
        SELECT
            COALESCE(nif_emisor, '')                                   AS nif,
            COALESCE(nombre_emisor, nif_emisor, fuente_id, 'Desconocido') AS nombre,
            ROUND(SUM(base_imponible), 2)  AS base_retencion,
            ROUND(SUM(cuota_retencion), 2) AS retenciones,
            ROUND(AVG(tipo_retencion), 2)  AS tipo_retencion_medio,
            MIN(fecha) AS primera_factura,
            MAX(fecha) AS ultima_factura,
            COUNT(*)   AS num_facturas
        FROM facturas
        WHERE tipo = 'recibida'
          AND cuota_retencion > 0
          AND fecha >= '{fecha_desde}' AND fecha <= '{fecha_hasta}'
        GROUP BY COALESCE(nif_emisor, nombre_emisor, fuente_id)
        ORDER BY retenciones DESC
    """)

    perceptores = [
        {
            "nif":                   r["nif"],
            "nombre":                r["nombre"],
            "clave":                 "G",  # actividades profesionales
            "subclave":              "01",
            "base_retencion":        r["base_retencion"],
            "retenciones":           r["retenciones"],
            "tipo_retencion_medio":  r["tipo_retencion_medio"],
            "num_facturas":          r["num_facturas"],
            "primera_factura":       r["primera_factura"],
            "ultima_factura":        r["ultima_factura"],
        }
        for r in perceptores_rows
    ]

    # ── Desglose trimestral ───────────────────────────────────────────────────
    trimestres = {}
    for q, (fd, fh) in [
        ("Q1", (f"{ejercicio}-01-01", f"{ejercicio}-03-31")),
        ("Q2", (f"{ejercicio}-04-01", f"{ejercicio}-06-30")),
        ("Q3", (f"{ejercicio}-07-01", f"{ejercicio}-09-30")),
        ("Q4", (f"{ejercicio}-10-01", f"{ejercicio}-12-31")),
    ]:
        r = db.raw_query(f"""
            SELECT
                COUNT(DISTINCT COALESCE(nif_emisor, nombre_emisor, fuente_id)) AS n,
                ROUND(SUM(base_imponible), 2)  AS base,
                ROUND(SUM(cuota_retencion), 2) AS ret
            FROM facturas
            WHERE tipo = 'recibida'
              AND cuota_retencion > 0
              AND fecha >= '{fd}' AND fecha <= '{fh}'
        """)[0]
        trimestres[q] = {
            "n_perceptores": r["n"] or 0,
            "base":          r["base"] or 0.0,
            "retenciones":   r["ret"] or 0.0,
        }

    advertencias = []
    sin_nif = [p for p in perceptores if not p["nif"]]
    if sin_nif:
        advertencias.append(
            f"{len(sin_nif)} perceptor(es) sin NIF identificado — "
            "revisa facturas de: " + ", ".join(p["nombre"] for p in sin_nif[:3])
        )

    return {
        "modelo": "190",
        "ejercicio": ejercicio,
        "periodo": "anual",
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "empresa_nif": config.EMPRESA_NIF,
        "empresa_nombre": config.EMPRESA_NOMBRE,
        "casillas": {
            "n_perceptores":     n_perceptores,
            "base_total":        base_total,
            "retenciones_total": retenciones_total,
        },
        "perceptores":  perceptores,
        "trimestres":   trimestres,
        "advertencias": advertencias,
        "resumen": {
            "n_perceptores":  n_perceptores,
            "base_total":     base_total,
            "a_ingresar":     retenciones_total,
        },
    }
