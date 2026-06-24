"""
Exportación de modelos fiscales a XML y CSV.

Los XML generados siguen la estructura de casillas de la AEAT pero NO son
el formato oficial de importación directa (ese requiere certificado
digital + conexión a Sede Electrónica). Sirven de referencia para
rellenar el formulario web de la AEAT o para entregar al asesor fiscal.

Formatos producidos:
  303 / 111  → XML  (estructura de casillas AEAT)
  200        → JSON (con todas las casillas y advertencias)
  facturas   → CSV  (para importar en Excel o enviar a gestoría)
"""
from __future__ import annotations

import csv
import io
import json
from datetime import date
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import Element, SubElement, indent, tostring

import config
from database import db
from tools.tax_models import calculate_303, calculate_111
from tools.modelo_200 import calculate_200
from tools.modelo_390 import calculate_390
from tools.modelo_190 import calculate_190

_PERIODOS_AEAT = {"Q1": "1T", "Q2": "2T", "Q3": "3T", "Q4": "4T", "anual": "0A"}


# ── Modelo 303 → XML ──────────────────────────────────────────────────────────

def export_303_xml(ejercicio: int, periodo: str) -> str:
    datos = calculate_303(ejercicio, periodo)
    c = datos["casillas"]

    root = Element("T30300")
    _t(root, "Ejercicio",    str(ejercicio))
    _t(root, "Periodo",      _periodo_aeat(periodo))
    _t(root, "NIF",          config.EMPRESA_NIF)
    _t(root, "RazonSocial",  config.EMPRESA_NOMBRE)

    dev = SubElement(root, "IVADevengado")
    _t(dev, "C01_BaseGeneral",         _n(c["01_base_general"]))
    _t(dev, "C02_CuotaGeneral",        _n(c["02_cuota_general"]))
    _t(dev, "C03_BaseReducido",        _n(c["03_base_reducido"]))
    _t(dev, "C04_CuotaReducido",       _n(c["04_cuota_reducido"]))
    _t(dev, "C05_BaseSuperreducido",   _n(c["05_base_superreducido"]))
    _t(dev, "C06_CuotaSuperreducido",  _n(c["06_cuota_superreducido"]))
    _t(dev, "C27_TotalDevengado",      _n(c["27_total_devengado"]))

    ded = SubElement(root, "IVADeducible")
    _t(ded, "C28_CuotasSoportadas",    _n(c["28_cuotas_soportadas"]))
    _t(ded, "C29_BasesSoportadas",     _n(c["29_bases_soportadas"]))
    _t(ded, "C46_TotalDeducible",      _n(c["46_total_deducible"]))

    res = SubElement(root, "Resultado")
    _t(res, "C64_Resultado",           _n(c["64_resultado"]))
    _t(res, "Signo",                   datos["resumen"]["signo"])

    _t(root, "FechaGeneracion", date.today().isoformat())
    indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(root, encoding="unicode")


# ── Modelo 111 → XML ──────────────────────────────────────────────────────────

def export_111_xml(ejercicio: int, periodo: str) -> str:
    datos = calculate_111(ejercicio, periodo)
    c = datos["casillas"]

    root = Element("T11100")
    _t(root, "Ejercicio",    str(ejercicio))
    _t(root, "Periodo",      _periodo_aeat(periodo))
    _t(root, "NIF",          config.EMPRESA_NIF)
    _t(root, "RazonSocial",  config.EMPRESA_NOMBRE)

    prof = SubElement(root, "ActividadesProfesionales")
    _t(prof, "C10_Perceptores",    str(c["10_perceptores_prof"]))
    _t(prof, "C11_BaseRetencion",  _n(c["11_base_prof"]))
    _t(prof, "C12_Retenciones",    _n(c["12_retenciones_prof"]))

    _t(root, "C28_TotalIngresar",  _n(c["28_total_ingresar"]))
    _t(root, "FechaGeneracion",    date.today().isoformat())
    indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(root, encoding="unicode")


# ── Modelo 390 → XML ──────────────────────────────────────────────────────────

def export_390_xml(ejercicio: int) -> str:
    datos = calculate_390(ejercicio)
    c = datos["casillas"]

    root = Element("T39000")
    _t(root, "Ejercicio",   str(ejercicio))
    _t(root, "Periodo",     "0A")
    _t(root, "NIF",         config.EMPRESA_NIF)
    _t(root, "RazonSocial", config.EMPRESA_NOMBRE)

    dev = SubElement(root, "IVADevengado")
    _t(dev, "C01_BaseGeneral",          _n(c["01_base_general"]))
    _t(dev, "C02_CuotaGeneral",         _n(c["02_cuota_general"]))
    _t(dev, "C03_BaseReducido",         _n(c["03_base_reducido"]))
    _t(dev, "C04_CuotaReducido",        _n(c["04_cuota_reducido"]))
    _t(dev, "C05_BaseSuperreducido",    _n(c["05_base_superreducido"]))
    _t(dev, "C06_CuotaSuperreducido",   _n(c["06_cuota_superreducido"]))
    _t(dev, "C09_TotalBaseDevengada",   _n(c["09_total_bases_devengadas"]))
    _t(dev, "C27_TotalDevengado",       _n(c["27_total_devengado"]))

    ded = SubElement(root, "IVADeducible")
    _t(ded, "C28_CuotasSoportadas",     _n(c["28_cuotas_soportadas"]))
    _t(ded, "C29_BasesSoportadas",      _n(c["29_bases_soportadas"]))
    _t(ded, "C46_TotalDeducible",       _n(c["46_total_deducible"]))

    res = SubElement(root, "Resultado")
    _t(res, "C64_ResultadoAnual",       _n(c["64_resultado_anual"]))
    _t(res, "C65_PctEstado",            _n(c["65_pct_estado"]))
    _t(res, "C66_ResultadoEstado",      _n(c["66_resultado_estado"]))
    _t(res, "C69_SumaTrimestral",       _n(c["69_suma_trimestral"]))
    _t(res, "C71_ResultadoFinal",       _n(c["71_resultado_final"]))
    _t(res, "Signo",                    datos["resumen"]["signo"])

    tri = SubElement(root, "DesgloseTrimestral")
    for q, td in datos["trimestres"].items():
        qe = SubElement(tri, f"Trimestre_{q}")
        _t(qe, "Resultado",   _n(td["resultado"]))
        _t(qe, "AIngresar",   _n(td["a_ingresar"]))
        _t(qe, "ACompensar",  _n(td["a_compensar"]))

    _t(root, "FechaGeneracion", date.today().isoformat())
    indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(root, encoding="unicode")


# ── Modelo 190 → XML ──────────────────────────────────────────────────────────

def export_190_xml(ejercicio: int) -> str:
    datos = calculate_190(ejercicio)
    c = datos["casillas"]

    root = Element("T19000")
    _t(root, "Ejercicio",   str(ejercicio))
    _t(root, "Periodo",     "0A")
    _t(root, "NIF",         config.EMPRESA_NIF)
    _t(root, "RazonSocial", config.EMPRESA_NOMBRE)

    resumen = SubElement(root, "Resumen")
    _t(resumen, "TotalPerceptores",  str(c["n_perceptores"]))
    _t(resumen, "TotalBase",         _n(c["base_total"]))
    _t(resumen, "TotalRetenciones",  _n(c["retenciones_total"]))

    perceps = SubElement(root, "Perceptores")
    for p in datos["perceptores"]:
        pe = SubElement(perceps, "Perceptor")
        _t(pe, "NIF",               p["nif"] or "SIN-NIF")
        _t(pe, "Nombre",            p["nombre"])
        _t(pe, "Clave",             p["clave"])
        _t(pe, "Subclave",          p["subclave"])
        _t(pe, "BaseRetencion",     _n(p["base_retencion"]))
        _t(pe, "Retenciones",       _n(p["retenciones"]))
        _t(pe, "TipoMedio",         _n(p["tipo_retencion_medio"]))
        _t(pe, "NumFacturas",       str(p["num_facturas"]))

    tri = SubElement(root, "DesgloseTrimestral")
    for q, td in datos["trimestres"].items():
        qe = SubElement(tri, f"Trimestre_{q}")
        _t(qe, "NPerceptores",  str(td["n_perceptores"]))
        _t(qe, "Base",          _n(td["base"]))
        _t(qe, "Retenciones",   _n(td["retenciones"]))

    if datos["advertencias"]:
        adv = SubElement(root, "Advertencias")
        for a in datos["advertencias"]:
            _t(adv, "Advertencia", a)

    _t(root, "FechaGeneracion", date.today().isoformat())
    indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(root, encoding="unicode")


# ── Modelo 200 → JSON ─────────────────────────────────────────────────────────

def export_200_json(
    ejercicio: int,
    tipo_gravamen: float = 25.0,
    ajustes_fiscales: float = 0.0,
    bins_anteriores: float = 0.0,
    deducciones: float = 0.0,
) -> str:
    datos = calculate_200(
        ejercicio,
        tipo_gravamen=tipo_gravamen,
        ajustes_fiscales=ajustes_fiscales,
        bins_anteriores=bins_anteriores,
        deducciones=deducciones,
    )
    return json.dumps(datos, indent=2, ensure_ascii=False)


# ── Facturas → CSV ────────────────────────────────────────────────────────────

def export_facturas_csv(
    fecha_desde: str,
    fecha_hasta: str,
    tipo: str | None = None,
) -> str:
    """Exporta facturas del período a CSV para Excel o gestoría."""
    conds = [f"fecha >= '{fecha_desde}'", f"fecha <= '{fecha_hasta}'"]
    if tipo:
        conds.append(f"tipo = '{tipo}'")
    facturas = db.raw_query(
        f"SELECT * FROM facturas WHERE {' AND '.join(conds)} ORDER BY fecha, tipo"
    )
    if not facturas:
        return ""

    cols = [
        "tipo", "numero", "fecha", "nif_emisor", "nombre_emisor",
        "nif_receptor", "nombre_receptor", "base_imponible", "tipo_iva",
        "cuota_iva", "tipo_retencion", "cuota_retencion", "total", "concepto", "fuente",
    ]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(facturas)
    return buf.getvalue()


# ── Función unificada para el agente ─────────────────────────────────────────

def export_model(
    modelo: str,
    ejercicio: int,
    periodo: str = "anual",
    output_path: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Genera el archivo de exportación para el modelo indicado.

    modelo:  '303' | '111' → XML
             '200'         → JSON
             'facturas'    → CSV  (kwargs: fecha_desde, fecha_hasta, tipo)

    Si output_path se especifica, guarda el fichero en disco.
    Devuelve siempre el contenido como string en 'contenido'.
    """
    modelo = modelo.upper()

    if modelo == "303":
        contenido = export_303_xml(ejercicio, periodo)
        ext = "xml"
    elif modelo == "111":
        contenido = export_111_xml(ejercicio, periodo)
        ext = "xml"
    elif modelo == "390":
        contenido = export_390_xml(ejercicio)
        ext = "xml"
    elif modelo == "190":
        contenido = export_190_xml(ejercicio)
        ext = "xml"
    elif modelo == "200":
        contenido = export_200_json(
            ejercicio,
            tipo_gravamen=kwargs.get("tipo_gravamen", 25.0),
            ajustes_fiscales=kwargs.get("ajustes_fiscales", 0.0),
            bins_anteriores=kwargs.get("bins_anteriores", 0.0),
            deducciones=kwargs.get("deducciones", 0.0),
        )
        ext = "json"
    elif modelo == "FACTURAS":
        contenido = export_facturas_csv(
            fecha_desde=kwargs["fecha_desde"],
            fecha_hasta=kwargs["fecha_hasta"],
            tipo=kwargs.get("tipo"),
        )
        ext = "csv"
    else:
        raise ValueError(f"Modelo no soportado para exportación: {modelo}. Use 303, 111, 390, 190, 200 o facturas.")

    if not output_path:
        output_path = f"modelo_{modelo.lower()}_{ejercicio}_{periodo}.{ext}"

    Path(output_path).write_text(contenido, encoding="utf-8")

    return {
        "modelo": modelo,
        "ejercicio": ejercicio,
        "periodo": periodo,
        "formato": ext,
        "fichero": output_path,
        "bytes": len(contenido.encode()),
        "contenido": contenido,
    }


# ── helpers ───────────────────────────────────────────────────────────────────

def _t(parent: Element, tag: str, text: str) -> None:
    SubElement(parent, tag).text = text


def _n(v: float) -> str:
    return f"{v:.2f}"


def _periodo_aeat(p: str) -> str:
    return _PERIODOS_AEAT.get(p, p)
