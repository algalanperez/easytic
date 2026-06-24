"""Tests de Modelos 303 y 111 (tools/tax_models.py)."""
from __future__ import annotations

import pytest

from tools.tax_models import calculate_303, calculate_111, generate_model_draft
import database.db as db


class TestCalculate303:
    def test_sin_facturas_resultado_cero(self, tmp_db):
        r = calculate_303(2025, "Q1")
        assert r["casillas"]["27_total_devengado"] == 0.0
        assert r["casillas"]["46_total_deducible"] == 0.0
        assert r["casillas"]["64_resultado"] == 0.0

    def test_iva_21_correcto(self, seeded_db):
        r = calculate_303(2025, "Q1")
        c = r["casillas"]
        assert c["01_base_general"] == 3000.0
        assert c["02_cuota_general"] == 630.0

    def test_iva_10_va_a_reducido(self, seeded_db):
        r = calculate_303(2025, "Q2")
        c = r["casillas"]
        assert c["03_base_reducido"] == 2000.0
        assert c["04_cuota_reducido"] == 200.0

    def test_deducible_de_recibidas(self, seeded_db):
        # Q1: recibida con cuota_iva=168
        r = calculate_303(2025, "Q1")
        assert r["casillas"]["28_cuotas_soportadas"] == 168.0

    def test_resultado_es_devengado_menos_deducible(self, seeded_db):
        r = calculate_303(2025, "Q1")
        c = r["casillas"]
        esperado = round(c["27_total_devengado"] - c["46_total_deducible"], 2)
        assert c["64_resultado"] == esperado

    def test_periodo_invalido_lanza_error(self, tmp_db):
        with pytest.raises(ValueError):
            calculate_303(2025, "Q5")

    def test_estructura_respuesta(self, tmp_db):
        r = calculate_303(2025, "Q1")
        assert r["modelo"] == "303"
        assert r["ejercicio"] == 2025
        assert r["periodo"] == "Q1"
        assert "casillas" in r and "resumen" in r
        assert "a_ingresar" in r["resumen"]
        assert "signo" in r["resumen"]


class TestCalculate111:
    def test_sin_retenciones_cero(self, tmp_db):
        r = calculate_111(2025, "Q1")
        assert r["casillas"]["10_perceptores_prof"] == 0
        assert r["casillas"]["28_total_ingresar"] == 0.0

    def test_cuenta_perceptores_unicos(self, seeded_db):
        # Q1: solo Freelance Juan
        r = calculate_111(2025, "Q1")
        assert r["casillas"]["10_perceptores_prof"] == 1

    def test_suma_retenciones(self, seeded_db):
        # Q1: cuota_retencion=120
        r = calculate_111(2025, "Q1")
        assert r["casillas"]["12_retenciones_prof"] == 120.0

    def test_perceptor_sin_nif_usa_fuente_id(self, tmp_db):
        from tools.db_tools import tool_upsert_factura
        # Factura recibida sin NIF ni nombre de emisor
        tool_upsert_factura({
            "tipo": "recibida", "fecha": "2025-02-01",
            "base_imponible": 500.0, "tipo_iva": 21, "cuota_iva": 105.0,
            "tipo_retencion": 15.0, "cuota_retencion": 75.0, "total": 530.0,
            "fuente": "test", "fuente_id": "sin_nif_001",
            "nif_emisor": None, "nombre_emisor": None,
            "nif_receptor": "B12345678", "nombre_receptor": "EasyTic SL",
            "numero": "X-01", "concepto": "Sin NIF",
        })
        r = calculate_111(2025, "Q1")
        # debe contar como 1 perceptor usando fuente_id como fallback
        assert r["casillas"]["10_perceptores_prof"] == 1

    def test_periodo_invalido_lanza_error(self, tmp_db):
        with pytest.raises(ValueError):
            calculate_111(2025, "Q0")


class TestGenerateModelDraft:
    def test_guarda_en_liquidaciones(self, tmp_db):
        generate_model_draft("303", 2025, "Q1")
        rows = db.list_liquidaciones()
        assert len(rows) == 1
        assert rows[0]["modelo"] == "303"
        assert rows[0]["estado"] == "borrador"

    def test_modelo_invalido_lanza_error(self, tmp_db):
        with pytest.raises(ValueError):
            generate_model_draft("999", 2025, "Q1")

    def test_upsert_no_duplica(self, tmp_db):
        generate_model_draft("303", 2025, "Q1")
        generate_model_draft("303", 2025, "Q1")
        assert len(db.list_liquidaciones()) == 1
