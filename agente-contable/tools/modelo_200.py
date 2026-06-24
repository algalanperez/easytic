"""
Cálculo del Modelo 200 — Impuesto de Sociedades (IS) anual.

Casillas implementadas:
  01  — Resultado contable (ingresos − gastos de las facturas)
  550 — Base imponible previa (resultado + ajustes fiscales)
  552 — Base imponible del período (tras compensar BINs)
  562 — Tipo de gravamen (%)
  599 — Cuota íntegra
  601 — Cuota líquida (tras deducciones)
  610 — Retenciones e ingresos a cuenta soportados
  621 — Cuota diferencial (a ingresar / a devolver)

Limitación deliberada: ajustes fiscales, BINs y deducciones no pueden
derivarse sólo de facturas — deben introducirse manualmente o mediante
el agente. El módulo genera advertencias cuando faltan.
"""
from __future__ import annotations

from typing import Any

import config
from database import db

TIPO_GENERAL: float = 25.0   # % tipo general para SL/SA
TIPO_NUEVA:   float = 15.0   # % primeros 2 ejercicios con base imponible positiva


def calculate_200(
    ejercicio: int,
    tipo_gravamen: float = TIPO_GENERAL,
    ajustes_fiscales: float = 0.0,      # correcciones al resultado contable (+/−)
    bins_anteriores: float = 0.0,       # bases imponibles negativas a compensar
    deducciones: float = 0.0,           # deducciones cuota (I+D, inversión, etc.)
) -> dict[str, Any]:
    """
    Calcula el Modelo 200 para el ejercicio indicado a partir de las
    facturas registradas en la BD más los ajustes manuales opcionales.
    """
    fecha_desde = f"{ejercicio}-01-01"
    fecha_hasta = f"{ejercicio}-12-31"

    # Ingresos — suma de bases de facturas emitidas
    ingresos = _sum_base("emitida", fecha_desde, fecha_hasta)
    # Gastos — suma de bases de facturas recibidas
    gastos = _sum_base("recibida", fecha_desde, fecha_hasta)
    # Retenciones soportadas (en facturas emitidas donde el cliente retuvo IRPF)
    retenciones = _sum_retencion("emitida", fecha_desde, fecha_hasta)

    resultado_contable = round(ingresos - gastos, 2)
    base_previa        = round(resultado_contable + ajustes_fiscales, 2)
    base_imponible     = round(max(base_previa - bins_anteriores, 0.0), 2)
    cuota_integra      = round(base_imponible * tipo_gravamen / 100, 2) if base_imponible > 0 else 0.0
    cuota_liquida      = round(max(cuota_integra - deducciones, 0.0), 2)
    cuota_diferencial  = round(cuota_liquida - retenciones, 2)

    return {
        "modelo":       "200",
        "ejercicio":    ejercicio,
        "periodo":      "anual",
        "fecha_desde":  fecha_desde,
        "fecha_hasta":  fecha_hasta,
        "empresa_nif":    config.EMPRESA_NIF,
        "empresa_nombre": config.EMPRESA_NOMBRE,
        "inputs": {
            "ingresos":          ingresos,
            "gastos":            gastos,
            "ajustes_fiscales":  ajustes_fiscales,
            "bins_anteriores":   bins_anteriores,
            "deducciones":       deducciones,
            "tipo_gravamen":     tipo_gravamen,
        },
        "casillas": {
            "01_resultado_contable":     resultado_contable,
            "550_base_imponible_previa": base_previa,
            "552_base_imponible":        base_imponible,
            "562_tipo_gravamen":         tipo_gravamen,
            "599_cuota_integra":         cuota_integra,
            "601_cuota_liquida":         cuota_liquida,
            "610_retenciones":           retenciones,
            "621_cuota_diferencial":     cuota_diferencial,
        },
        "resumen": {
            "resultado_contable": resultado_contable,
            "base_imponible":     base_imponible,
            "cuota_a_pagar":      max(cuota_diferencial, 0.0),
            "a_devolver":         abs(min(cuota_diferencial, 0.0)),
            "signo":              "ingreso" if cuota_diferencial >= 0 else "devolucion",
        },
        "advertencias": _warnings(resultado_contable, ajustes_fiscales, deducciones),
    }


# ── helpers ───────────────────────────────────────────────────────────────────

def _sum_base(tipo: str, desde: str, hasta: str) -> float:
    rows = db.raw_query(f"""
        SELECT ROUND(SUM(base_imponible), 2) AS total
        FROM facturas
        WHERE tipo = '{tipo}' AND fecha >= '{desde}' AND fecha <= '{hasta}'
    """)
    return rows[0]["total"] or 0.0


def _sum_retencion(tipo: str, desde: str, hasta: str) -> float:
    rows = db.raw_query(f"""
        SELECT ROUND(SUM(cuota_retencion), 2) AS total
        FROM facturas
        WHERE tipo = '{tipo}' AND cuota_retencion > 0
          AND fecha >= '{desde}' AND fecha <= '{hasta}'
    """)
    return rows[0]["total"] or 0.0


def _warnings(resultado: float, ajustes: float, deducciones: float) -> list[str]:
    w = []
    if resultado < 0:
        w.append(
            "Resultado contable negativo. Las BINs generadas pueden compensarse en "
            "ejercicios futuros (art. 26 LIS). Consúltalo con tu asesor."
        )
    if ajustes == 0.0:
        w.append(
            "No se han aplicado ajustes fiscales. Revisa: amortizaciones, gastos no "
            "deducibles, operaciones vinculadas, diferencias temporarias (art. 11-26 LIS)."
        )
    if deducciones == 0.0 and resultado > 0:
        w.append(
            "No se han aplicado deducciones en cuota. Verifica: I+D+i (art. 35), "
            "inversión en vehículos EV, Reserva de Capitalización (art. 25 LIS)."
        )
    return w
