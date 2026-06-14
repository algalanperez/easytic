"""
Calendario fiscal español y lógica de alertas de vencimientos.
"""
from datetime import date, datetime
from typing import Any


CALENDAR: dict[str, list[dict]] = {
    # modelo → lista de {periodo, vencimiento_fmt, descripcion}
    "303": [
        {"periodo": "Q1", "mes": 4, "dia": 20, "descripcion": "IVA 1T (enero-marzo)"},
        {"periodo": "Q2", "mes": 7, "dia": 20, "descripcion": "IVA 2T (abril-junio)"},
        {"periodo": "Q3", "mes": 10, "dia": 20, "descripcion": "IVA 3T (julio-septiembre)"},
        {"periodo": "Q4", "mes": 1, "dia": 30, "año_sig": True, "descripcion": "IVA 4T (octubre-diciembre)"},
    ],
    "390": [
        {"periodo": "anual", "mes": 1, "dia": 30, "año_sig": True, "descripcion": "Resumen anual IVA"},
    ],
    "111": [
        {"periodo": "Q1", "mes": 4, "dia": 20, "descripcion": "Retenciones IRPF 1T"},
        {"periodo": "Q2", "mes": 7, "dia": 20, "descripcion": "Retenciones IRPF 2T"},
        {"periodo": "Q3", "mes": 10, "dia": 20, "descripcion": "Retenciones IRPF 3T"},
        {"periodo": "Q4", "mes": 1, "dia": 20, "año_sig": True, "descripcion": "Retenciones IRPF 4T"},
    ],
    "190": [
        {"periodo": "anual", "mes": 1, "dia": 31, "año_sig": True, "descripcion": "Resumen anual retenciones"},
    ],
    "200": [
        {"periodo": "anual", "mes": 7, "dia": 25, "descripcion": "Impuesto de Sociedades"},
    ],
}

QUARTER_RANGES = {
    "Q1": ("01-01", "03-31"),
    "Q2": ("04-01", "06-30"),
    "Q3": ("07-01", "09-30"),
    "Q4": ("10-01", "12-31"),
}


def get_tax_calendar(ejercicio: int) -> list[dict]:
    """Devuelve todos los vencimientos del ejercicio ordenados por fecha."""
    result = []
    for modelo, entries in CALENDAR.items():
        for e in entries:
            año = ejercicio + 1 if e.get("año_sig") else ejercicio
            try:
                venc = date(año, e["mes"], e["dia"])
            except ValueError:
                continue
            result.append({
                "modelo": modelo,
                "periodo": e["periodo"],
                "vencimiento": venc.isoformat(),
                "descripcion": e["descripcion"],
                "ejercicio": ejercicio,
            })
    return sorted(result, key=lambda x: x["vencimiento"])


def get_upcoming_deadlines(days_ahead: int = 30, ejercicio: int | None = None) -> list[dict]:
    """Devuelve vencimientos que caen en los próximos `days_ahead` días."""
    today = date.today()
    año = ejercicio or today.year
    # Incluye el ejercicio actual y el siguiente por si el año ya ha cambiado
    calendar = get_tax_calendar(año - 1) + get_tax_calendar(año)
    upcoming = []
    for entry in calendar:
        venc = date.fromisoformat(entry["vencimiento"])
        delta = (venc - today).days
        if 0 <= delta <= days_ahead:
            entry["dias_restantes"] = delta
            upcoming.append(entry)
    return sorted(upcoming, key=lambda x: x["vencimiento"])


def quarter_of_date(d: str) -> str:
    """Devuelve 'Q1'...'Q4' dado 'YYYY-MM-DD'."""
    month = int(d[5:7])
    return f"Q{(month - 1) // 3 + 1}"


def quarter_date_range(ejercicio: int, quarter: str) -> tuple[str, str]:
    """Devuelve (fecha_inicio, fecha_fin) del trimestre en formato YYYY-MM-DD."""
    start_m, end_m = QUARTER_RANGES[quarter]
    return f"{ejercicio}-{start_m}", f"{ejercicio}-{end_m}"
