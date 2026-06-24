"""
Cálculo de los modelos fiscales españoles y generación de borradores.

Modelo 303 — Autoliquidación trimestral del IVA
Modelo 111 — Retenciones e ingresos a cuenta del IRPF (actividades profesionales)
Modelo 200 — Impuesto de Sociedades anual (delegado a tools.modelo_200)
"""
from __future__ import annotations

from typing import Any

import config
from database import db
from tools.tax_calendar import quarter_date_range, QUARTER_RANGES


# ── Modelo 303 ────────────────────────────────────────────────────────────────

def calculate_303(ejercicio: int, periodo: str) -> dict[str, Any]:
    """
    Calcula las casillas del Modelo 303 para un trimestre o año completo.

    periodo: 'Q1' | 'Q2' | 'Q3' | 'Q4'

    Casillas implementadas:
      IVA devengado (facturas emitidas)
        01/02 — tipo general 21%
        03/04 — tipo reducido 10%
        05/06 — tipo superreducido 4%
        27    — total IVA devengado
      IVA deducible (facturas recibidas)
        28/29 — cuotas y bases operaciones interiores corrientes
        46    — total IVA deducible
      Resultado
        64    — resultado (27 − 46)
    """
    if periodo not in QUARTER_RANGES:
        raise ValueError(f"periodo debe ser Q1..Q4, recibido: {periodo!r}")

    fecha_desde, fecha_hasta = quarter_date_range(ejercicio, periodo)

    # ── IVA devengado (emitidas) ──
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

    total_devengado = round(cuota_21 + cuota_10 + cuota_4, 2)

    # ── IVA deducible (recibidas) ──
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

    resultado = round(total_devengado - cuota_deducible, 2)

    return {
        "modelo": "303",
        "ejercicio": ejercicio,
        "periodo": periodo,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "empresa_nif": config.EMPRESA_NIF,
        "empresa_nombre": config.EMPRESA_NOMBRE,
        "casillas": {
            # IVA devengado
            "01_base_general":         base_21,
            "02_cuota_general":        cuota_21,
            "03_base_reducido":        base_10,
            "04_cuota_reducido":       cuota_10,
            "05_base_superreducido":   base_4,
            "06_cuota_superreducido":  cuota_4,
            "27_total_devengado":      total_devengado,
            # IVA deducible
            "28_cuotas_soportadas":    cuota_deducible,
            "29_bases_soportadas":     base_deducible,
            "46_total_deducible":      cuota_deducible,
            # Resultado
            "64_resultado":            resultado,
        },
        "resumen": {
            "a_ingresar":   max(resultado, 0.0),
            "a_compensar":  abs(min(resultado, 0.0)),
            "signo":        "ingreso" if resultado >= 0 else "compensacion",
        },
    }


# ── Modelo 111 ────────────────────────────────────────────────────────────────

def calculate_111(ejercicio: int, periodo: str) -> dict[str, Any]:
    """
    Calcula las casillas del Modelo 111 para un trimestre.

    Incluye únicamente retenciones de actividades profesionales (autónomos/freelance)
    identificadas por cuota_retencion > 0 en facturas recibidas.

    Casillas implementadas:
      Rendimientos de actividades profesionales:
        10 — número de perceptores
        11 — base de retención
        12 — retenciones e ingresos a cuenta
      Total:
        28 — total a ingresar
    """
    if periodo not in QUARTER_RANGES:
        raise ValueError(f"periodo debe ser Q1..Q4, recibido: {periodo!r}")

    fecha_desde, fecha_hasta = quarter_date_range(ejercicio, periodo)

    rows = db.raw_query(f"""
        SELECT
            COUNT(DISTINCT COALESCE(nif_emisor, nombre_emisor, fuente_id)) AS n_perceptores,
            ROUND(SUM(base_imponible), 2)   AS base_retencion,
            ROUND(SUM(cuota_retencion), 2)  AS total_retencion
        FROM facturas
        WHERE tipo = 'recibida'
          AND cuota_retencion > 0
          AND fecha >= '{fecha_desde}' AND fecha <= '{fecha_hasta}'
    """)

    n_perceptores    = rows[0]["n_perceptores"]   or 0
    base_retencion   = rows[0]["base_retencion"]  or 0.0
    total_retencion  = rows[0]["total_retencion"] or 0.0

    return {
        "modelo": "111",
        "ejercicio": ejercicio,
        "periodo": periodo,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "empresa_nif": config.EMPRESA_NIF,
        "empresa_nombre": config.EMPRESA_NOMBRE,
        "casillas": {
            # Actividades profesionales (autónomos)
            "10_perceptores_prof":  n_perceptores,
            "11_base_prof":         base_retencion,
            "12_retenciones_prof":  total_retencion,
            # Total
            "28_total_ingresar":    total_retencion,
        },
        "resumen": {
            "n_perceptores": n_perceptores,
            "base_total":    base_retencion,
            "a_ingresar":    total_retencion,
        },
    }


# ── generate_model_draft ──────────────────────────────────────────────────────

def generate_model_draft(
    modelo: str,
    ejercicio: int,
    periodo: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Calcula el modelo fiscal, lo persiste en la tabla liquidaciones como borrador
    y devuelve el resultado completo.

    modelo:   '303' | '111' | '200'
    periodo:  'Q1'|'Q2'|'Q3'|'Q4' para 303/111; 'anual' para 200
    kwargs:   para Modelo 200 — ajustes_fiscales, bins_anteriores, deducciones, tipo_gravamen
    """
    from tools.modelo_200 import calculate_200
    from tools.modelo_390 import calculate_390
    from tools.modelo_190 import calculate_190

    modelo = modelo.strip()
    if modelo == "303":
        datos = calculate_303(ejercicio, periodo)
    elif modelo == "111":
        datos = calculate_111(ejercicio, periodo)
    elif modelo == "200":
        periodo = "anual"
        datos = calculate_200(ejercicio, **kwargs)
    elif modelo == "390":
        periodo = "anual"
        datos = calculate_390(ejercicio)
    elif modelo == "190":
        periodo = "anual"
        datos = calculate_190(ejercicio)
    else:
        raise ValueError(f"Modelo no soportado: {modelo!r}. Use '303', '111', '200', '390' o '190'.")

    db.upsert_liquidacion(modelo, ejercicio, periodo, datos)

    datos["_guardado"] = True
    datos["_mensaje"] = (
        f"Borrador del Modelo {modelo} {periodo}/{ejercicio} guardado en la base de datos."
    )
    return datos


# ── list_liquidaciones ────────────────────────────────────────────────────────

def list_liquidaciones(ejercicio: int | None = None) -> list[dict]:
    """Lista los borradores/liquidaciones guardados, opcionalmente filtrados por ejercicio."""
    return db.list_liquidaciones(ejercicio)
