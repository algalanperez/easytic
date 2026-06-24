"""
Modelo 390 — Declaración-Resumen Anual del IVA.

Es el consolidado anual de los cuatro Modelos 303 trimestrales.
Plazo: 30 de enero del año siguiente al ejercicio.

Casillas implementadas (estructura AEAT simplificada):
  IVA devengado (emitidas)
    01/02  — tipo general 21%
    03/04  — tipo reducido 10%
    05/06  — tipo superreducido 4%
    09     — suma de bases devengadas
    27     — total IVA devengado
  IVA deducible (recibidas)
    28     — cuotas soportadas operaciones interiores
    29     — bases soportadas
    46     — total IVA deducible
  Resultado anual
    64     — resultado anual (27 − 46)
    65     — porcentaje atribuible al Estado (100 % empresa estándar)
    66     — resultado atribuido al Estado (64 × 65 / 100)
    69     — suma resultados trimestrales presentados (303 Q1+Q2+Q3+Q4)
    71     — resultado final declaración (66 − 69)
  Desglose trimestral
    Incluido en 'trimestres' para referencia y casillas 77-84
"""
from __future__ import annotations

from typing import Any

import config
from database import db
from tools.tax_calendar import quarter_date_range
from tools.tax_models import calculate_303


def calculate_390(ejercicio: int) -> dict[str, Any]:
    """Calcula el Modelo 390 (resumen anual IVA) agregando los cuatro trimestres."""

    # ── Datos anuales directamente de BD ──────────────────────────────────────
    fecha_desde = f"{ejercicio}-01-01"
    fecha_hasta = f"{ejercicio}-12-31"

    rows_emit = db.raw_query(f"""
        SELECT
            tipo_iva,
            ROUND(SUM(base_imponible), 2) AS base,
            ROUND(SUM(cuota_iva), 2)      AS cuota
        FROM facturas
        WHERE tipo = 'emitida'
          AND fecha >= '{fecha_desde}' AND fecha <= '{fecha_hasta}'
        GROUP BY tipo_iva
        ORDER BY tipo_iva DESC
    """)

    base_21 = cuota_21 = 0.0
    base_10 = cuota_10 = 0.0
    base_4  = cuota_4  = 0.0
    for r in rows_emit:
        iva = float(r["tipo_iva"])
        if iva == 21.0:
            base_21, cuota_21 = r["base"], r["cuota"]
        elif iva == 10.0:
            base_10, cuota_10 = r["base"], r["cuota"]
        elif iva == 4.0:
            base_4, cuota_4 = r["base"], r["cuota"]

    rows_recv = db.raw_query(f"""
        SELECT
            ROUND(SUM(base_imponible), 2) AS base,
            ROUND(SUM(cuota_iva), 2)      AS cuota
        FROM facturas
        WHERE tipo = 'recibida'
          AND fecha >= '{fecha_desde}' AND fecha <= '{fecha_hasta}'
    """)
    base_deducible  = rows_recv[0]["base"]  or 0.0
    cuota_deducible = rows_recv[0]["cuota"] or 0.0

    # ── Casillas principales ──────────────────────────────────────────────────
    total_bases_devengadas = round(base_21 + base_10 + base_4, 2)
    total_devengado = round(cuota_21 + cuota_10 + cuota_4, 2)
    resultado_anual = round(total_devengado - cuota_deducible, 2)
    pct_estado      = 100.0
    resultado_estado = round(resultado_anual * pct_estado / 100, 2)

    # ── Suma de resultados trimestrales (casilla 69) ──────────────────────────
    trimestres = {}
    suma_trimestral = 0.0
    for q in ("Q1", "Q2", "Q3", "Q4"):
        t = calculate_303(ejercicio, q)
        res_q = t["casillas"]["64_resultado"]
        trimestres[q] = {
            "resultado":       res_q,
            "a_ingresar":      t["resumen"]["a_ingresar"],
            "a_compensar":     t["resumen"]["a_compensar"],
            "fecha_desde":     t["fecha_desde"],
            "fecha_hasta":     t["fecha_hasta"],
        }
        suma_trimestral = round(suma_trimestral + res_q, 2)

    resultado_final = round(resultado_estado - suma_trimestral, 2)

    return {
        "modelo": "390",
        "ejercicio": ejercicio,
        "periodo": "anual",
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "empresa_nif": config.EMPRESA_NIF,
        "empresa_nombre": config.EMPRESA_NOMBRE,
        "casillas": {
            # Devengado
            "01_base_general":          base_21,
            "02_cuota_general":         cuota_21,
            "03_base_reducido":         base_10,
            "04_cuota_reducido":        cuota_10,
            "05_base_superreducido":    base_4,
            "06_cuota_superreducido":   cuota_4,
            "09_total_bases_devengadas": total_bases_devengadas,
            "27_total_devengado":       total_devengado,
            # Deducible
            "28_cuotas_soportadas":     cuota_deducible,
            "29_bases_soportadas":      base_deducible,
            "46_total_deducible":       cuota_deducible,
            # Resultado
            "64_resultado_anual":       resultado_anual,
            "65_pct_estado":            pct_estado,
            "66_resultado_estado":      resultado_estado,
            "69_suma_trimestral":       suma_trimestral,
            "71_resultado_final":       resultado_final,
        },
        "trimestres": trimestres,
        "resumen": {
            "total_devengado":   total_devengado,
            "total_deducible":   cuota_deducible,
            "resultado_anual":   resultado_anual,
            "suma_trimestral":   suma_trimestral,
            "resultado_final":   resultado_final,
            "signo": "ingreso" if resultado_final >= 0 else "a_devolver",
        },
    }
