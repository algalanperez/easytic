"""Tests del calendario fiscal (tools/tax_calendar.py)."""
from __future__ import annotations

from tools.tax_calendar import (
    CALENDAR,
    get_tax_calendar,
    get_upcoming_deadlines,
    quarter_date_range,
    quarter_of_date,
)


class TestQuarterDateRange:
    def test_q1(self):
        assert quarter_date_range(2025, "Q1") == ("2025-01-01", "2025-03-31")

    def test_q2(self):
        assert quarter_date_range(2025, "Q2") == ("2025-04-01", "2025-06-30")

    def test_q3(self):
        assert quarter_date_range(2025, "Q3") == ("2025-07-01", "2025-09-30")

    def test_q4(self):
        assert quarter_date_range(2025, "Q4") == ("2025-10-01", "2025-12-31")

    def test_periodo_invalido(self):
        import pytest
        with pytest.raises((ValueError, KeyError)):
            quarter_date_range(2025, "Q5")


class TestQuarterOfDate:
    def test_enero_es_q1(self):
        assert quarter_of_date("2025-01-15") == "Q1"

    def test_abril_es_q2(self):
        assert quarter_of_date("2025-04-01") == "Q2"

    def test_julio_es_q3(self):
        assert quarter_of_date("2025-07-31") == "Q3"

    def test_octubre_es_q4(self):
        assert quarter_of_date("2025-10-01") == "Q4"

    def test_diciembre_es_q4(self):
        assert quarter_of_date("2025-12-31") == "Q4"


class TestGetTaxCalendar:
    def test_contiene_todos_los_modelos(self):
        cal = get_tax_calendar(2025)
        modelos = {d["modelo"] for d in cal}
        assert {"303", "111", "390", "190", "200"} <= modelos

    def test_ordenado_por_fecha(self):
        cal = get_tax_calendar(2025)
        fechas = [d["vencimiento"] for d in cal]
        assert fechas == sorted(fechas)

    def test_390_vence_en_enero_siguiente(self):
        cal = get_tax_calendar(2025)
        entry_390 = next(d for d in cal if d["modelo"] == "390")
        assert entry_390["vencimiento"].startswith("2026-01")

    def test_200_vence_en_julio(self):
        cal = get_tax_calendar(2025)
        entry_200 = next(d for d in cal if d["modelo"] == "200")
        assert "-07-" in entry_200["vencimiento"]


class TestGetUpcomingDeadlines:
    def test_filtra_por_dias(self):
        # Con 0 días no debe haber vencimientos futuros (todos ya pasaron en 2025)
        deadlines = get_upcoming_deadlines(days_ahead=0, ejercicio=2025)
        assert isinstance(deadlines, list)

    def test_incluye_campo_dias_restantes(self):
        deadlines = get_upcoming_deadlines(days_ahead=400, ejercicio=2025)
        if deadlines:
            assert "dias_restantes" in deadlines[0]
            assert "vencimiento" in deadlines[0]
            assert "modelo" in deadlines[0]
